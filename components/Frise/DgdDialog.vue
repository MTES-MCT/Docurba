
<template>
  <v-dialog id="dgd-dialog" v-model="dialog" width="1000">
    <template #activator="{ on, attrs }">
      <v-list-item link v-bind="attrs" v-on="on">
        <v-list-item-title>
          DGD
        </v-list-item-title>
      </v-list-item>
    </template>

    <v-card>
      <div class="text-right pr-2 pt-2">
        <v-btn color="primary" text @click="dialog = false">
          Fermer x
        </v-btn>
      </div>

      <v-card-title class="text-h5 align-start pl-8 ">
        <div class="font-weight-bold">
          DGD
        </div>
      </v-card-title>

      <v-card-text class="pt-4">
        <v-container fluid class="px-0">
          <v-row v-if="(!versements || versements.length === 0) && !showVersementForm">
            <v-col cols="12" class="text-center py-8 typo--text">
              <div class="font-weight-bold text-h5">
                Aucun versement
              </div>
              <div class="mb-4">
                Aucun versement n’a été entré pour cette procédure.
              </div>
              <v-btn depressed color="primary" @click="showVersementForm = true">
                Ajouter un versement
              </v-btn>
            </v-col>
          </v-row>
          <div v-else>
            <v-expansion-panels accordion flat class="dgd-exp-pan">
              <template v-for="(versement, i) in versements">
                <FriseDgdVersExpPanel
                  :key="`versement-${i}`"
                  class="mb-4"
                  :versement="versement"
                  @delete="deleteVersement"
                  @save-step="saveStep"
                  @delete-step="deleteStep"
                />
              </template>
            </v-expansion-panels>
            <div v-if="showVersementForm">
              <div class="font-weight-bold typo--text mb-1">
                Ajouter un versement
              </div>
              <FriseDgdVersementForm @add="addNewVersement" @save="addNewVersement(arguments[0])" @cancel="showVersementForm = false" />
            </div>
            <v-row>
              <v-col cols="12">
                <div>
                  <div v-if="!showVersementForm" class="my-6">
                    <v-btn depressed color="primary" @click="showVersementForm = true">
                      Ajouter un versement
                    </v-btn>
                  </div>
                  <div class="mb-4">
                    Commentaire général
                  </div>
                  <span v-if="!showCommentForm && !generalComment " style="cursor: pointer;" class="primary--text font-weight-bold" text @click="clickAddCom">
                    Ajouter un commentaire
                  </span>
                  <div v-else>
                    <InputsEditableText
                      v-model="generalComment"
                      hide-label
                      :edit="!generalComment "
                      label="Commentaire:"
                      compact
                      @confirmed="saveComment"
                      @cancel="cancelShowCommentForm"
                    />
                  </div>
                </div>
              </v-col>
            </v-row>
          </div>
        </v-container>
      </v-card-text>
    </v-card>
    <v-snackbar
      v-model="snackbar"
      top
      color="success"
      outlined
      :timeout="3000"
    >
      <v-icon small color="success" class="mr-2">
        {{ icons.mdiCheckCircle }}
      </v-icon>

      {{ snackbarText }}
    </v-snackbar>
  </v-dialog>
</template>
<script>
import { mdiCheck, mdiClose, mdiDotsVertical, mdiCheckCircle } from '@mdi/js'

export default
{
  name: 'DgdDialog',
  props: {},
  data () {
    return {
      showCommentForm: false,
      showVersementForm: false,
      generalComment: '',
      versements: [],
      snackbar: false,
      snackbarText: null,
      dialog: false,
      icons: {
        mdiCheck,
        mdiClose,
        mdiDotsVertical,
        mdiCheckCircle
      }
    }
  },
  computed: {

  },
  async mounted () {
    await this.refreshVersements()
  },
  methods: {
    clickAddCom () {
      this.showCommentForm = true
    },
    async saveComment () {
      console.log('SAVE this.generalComment: ', this.generalComment)
      const { error } = await this.$supabase.from('procedures').update({ comment_dgd: this.generalComment }).eq('id', this.$route.params.procedureId)
      if (error) { console.log('ERROR UPDATE COMMENT: ', error) }
      if (!this.generalComment) { this.showCommentForm = false }
    },
    cancelShowCommentForm () {
      console.log('cancel showFORm')
      console.log('this.generalComment: ', this.generalComment)
      if (!this.generalComment) { this.showCommentForm = false }
    },
    async refreshVersements () {
      const { data: versementsData } = await this.$supabase.from('versements').select('*, etapes_versement(*)').eq('procedure_id', this.$route.params.procedureId)
      const { data: procedureData } = await this.$supabase.from('procedures').select('id, comment_dgd').eq('id', this.$route.params.procedureId)

      this.generalComment = procedureData[0].comment_dgd
      this.versements = versementsData
    },
    async deleteVersement (versement) {
      this.versements = this.versements.filter(e => e.id !== versement.id)
      await this.$supabase.from('versements').delete().eq('id', versement.id)
      this.snackbarText = 'Versement supprimée.'
    },
    async addNewVersement (versement) {
      this.showVersementForm = false
      const { data, error } = await this.$supabase.from('versements').insert({ amount: versement.amount, year: versement.year, category: versement.category, comment: versement.comment, procedure_id: this.$route.params.procedureId }).select()
      if (error) { console.log('ERROR INSERT: ', error) }
      this.versements = [...this.versements, data[0]]
    },
    async deleteStep (toDeleteStep) {
      console.log('deleteStep: ', toDeleteStep)
      await this.$supabase.from('etapes_versement').delete().eq('id', toDeleteStep.id)
      await this.refreshVersements()
      this.snackbarText = 'Étape de versement supprimée.'
    },
    async saveStep ({ step, versement }) {
      // TODO: Faire un upsert
      await this.$supabase.from('etapes_versement').insert({
        name: step.name,
        versement_id: versement.id,
        is_done: step.isDone,
        category: step.category,
        amount: step.amount,
        date: '01/07/1992'// step.date
      }).select()
      await this.refreshVersements()
    }
  }
}
</script>

<style>
#dgd-dialog .v-expansion-panel-content > .v-expansion-panel-content__wrap{
  padding: 0px!important;
}

.dgd-exp-pan .v-expansion-panel-header{
  border: 1px solid var(--v-grey-base) ;
}

.dgd-exp-pan .v-expansion-panel-content{
  border: 1px solid var(--v-grey-base) ;
  border-top: none;
}
</style>
