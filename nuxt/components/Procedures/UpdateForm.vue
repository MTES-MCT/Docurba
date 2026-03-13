<template>
  <VGlobalLoader v-if="!isLoaded" />
  <validation-observer v-else :ref="`observerUpdateProcedure`" v-slot="{ handleSubmit, invalid }">
    <form @submit.prevent="handleSubmit(updateProcedure)">
      <v-container class="pa-0">
        <v-row>
          <v-col cols="6" class="pb-0">
            <v-alert dense text type="info" class="mb-2"  >
              Mettez à jour l'objet dès maintenant ! La modification des autres champs sera disponible prochainement.
            </v-alert>
          </v-col>
        </v-row>
        <v-row>
          <v-col cols="6" class="pt-0 pb-2">
            <v-select
              v-model="topics"
              :hide-details="topicOtherCommentSelected"
              filled
              multiple
              label="Objet de la procédure"
              return-object
              :items="topicsItems"
              />
          </v-col>
        </v-row>
        <v-row>
          <v-col v-if="topicOtherCommentSelected" cols="6" class="pt-0 pb-2">
            <validation-provider v-slot="{ errors }" name="Details de la procédure" rules="required">
              <v-text-field v-model="topicOtherComment" :error-messages="errors" filled label="Description de l’objet de la procédure" />
            </validation-provider>
          </v-col>
        </v-row>
        <v-row>
          <v-col cols="12" class="d-flex">
            <v-btn
              type="submit"
              color="primary"
              depressed
              :loading="loadingSave"
              :disabled="invalid"
            >
              Modifier la procédure
            </v-btn>
          </v-col>
        </v-row>
      </v-container>
    </form>
  </validation-observer>
</template>

<script>
import { mdiInformationOutline, mdiOpenInNew } from '@mdi/js'
import FormInput from '@/mixins/FormInput.js'

export default {
  name: 'UpdateProcedureForm',
  mixins: [FormInput],
  props: {
    procedureId: {
      type: String,
      required: true
    }
  },
  data () {
    return {
      // Form data
      topics: [],
      topicsIdsOnMounted: [],
      topicsItems: [],
      topicOtherComment: '',
      icons: { mdiInformationOutline, mdiOpenInNew },
      loaded: false,
      loadingSave: false
    }
  },
  computed: {
    isLoaded () {
      return this.loaded && (this.procedure.is_principale || this.procedureParent !== null)
    },
    topicOtherCommentSelected () {
      return this.topics.some(e => e.text === 'Autre')
    }
  },
  async mounted () {
    try {
      const { data: resultProcedure } = await this.$supabase.from('procedures')
        .select('id, owner_id, secondary_procedure_of, doc_type, type, numero, name, is_principale, collectivite_porteuse_id, secondary_procedure_of(name, doc_type), procedures_perimetres(collectivite_code)')
        .eq('id', this.procedureId)
      const procedure = resultProcedure[0]

      // const { data: procedureTopics, error: errorProcedureTopics } = await this.$supabase.from('core_proceduretopic').select('core_topic(id,display_name)').eq('procedure_id', procedure.id)

      this.loaded = true
      this.procedure = procedure

      this.topicsItems = await this.getTopicsDefaultItems()
      const topicsResponse = await this.getTopics()
      this.topics = topicsResponse.topics
      this.topicsIdsOnMounted = topicsResponse.topics.map(e => e.value)
      this.topicOtherComment = topicsResponse.topicOtherComment
    } catch (error) {
      // eslint-disable-next-line no-console
      console.log(error)
    }
  },
  methods: {
    async updateProcedure () {
      this.loadingSave = true

      try {
        const { error } = await this.$supabase.from('procedures').update({
          last_updated_at: new Date().toISOString(),
          last_updated_by_id: this.$user.id
        }).eq('id', this.procedure.id).select()

        let topicsToInsert = this.topics.filter(e => !this.topicsIdsOnMounted.includes(e.value))
        if (topicsToInsert.length > 0) {
          topicsToInsert = topicsToInsert.map((e) => {
            return {
              topic_id: e.value,
              procedure_id: this.procedure.id,
              comment: e.text === 'Autre' ? this.topicOtherComment : ''
            }
          })
          await this.$supabase.from('core_proceduretopic').insert(topicsToInsert)
        }

        const topicsIdsToDelete = this.topicsIdsOnMounted.filter(e => !this.topics.map(t => t.value).includes(e))
        if (topicsIdsToDelete.length > 0) {
          await this.$supabase.from('core_proceduretopic').delete().in('topic_id', topicsIdsToDelete)
        }

        const topicsToUpdate = this.topics.filter(e => this.topicsIdsOnMounted.includes(e.value) && e.text === 'Autre')
        if (topicsToUpdate.length > 0) {
          await this.$supabase.from('core_proceduretopic').update({
            comment: this.topicOtherComment,
            updated_at: new Date().toISOString()
          }).eq('procedure_id', this.procedure.id).eq('topic_id', topicsToUpdate[0].value)
        }

        if (error) {
          // eslint-disable-next-line no-console
          console.log('errorInsertedProcedure: ', error)
        }

        this.$analytics({
          category: 'procedures',
          name: 'update_procedure',
          value: (this.procedure.name)
        })

        this.$router.back()
      } catch (error) {
        this.error = error
        // eslint-disable-next-line no-console
        console.log(error)
      } finally {
        this.loadingSave = false
      }
    },
    async getTopicsDefaultItems () {
      // TODO; same as in InsertForm. Move me elsewhere?
      let { data: topics } = await this.$supabase.from('core_topic').select('id,display_name,ui_rank')
      topics = topics.sort((a, b) => {
        return a.ui_rank > b.ui_rank
      })
      // Push first item to the end.
      topics.push(topics.shift())
      return topics.map((e) => {
        return { value: e.id, text: e.display_name }
      })
    },
    async getTopics () {
      const { data: topicsData } = await this.$supabase.from('core_proceduretopic').select('comment, core_topic(id,display_name,ui_rank)').eq('procedure_id', this.procedure.id)
      const topics = topicsData.map((e) => {
        return { value: e.core_topic.id, text: e.core_topic.display_name }
      })
      let topicOtherComment = ''
      const otherTopic = topicsData.filter(e => e.core_topic.display_name === 'Autre')
      if (otherTopic.length > 0) {
        topicOtherComment = otherTopic[0].comment
      }
      return {
        topics,
        topicOtherComment
      }
    }
  }

}
</script>

<style lang="scss">
.smaller-input-slot .v-input__slot{
  min-height: 55px !important;
}
</style>
