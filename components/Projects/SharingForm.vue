<template>
  <v-row>
    <v-col cols="12">
      <v-text-field
        v-model="emailsInput"
        filled
        hide-details
        label="email"
        :append-icon="icons.mdiShare"
        @click:append="shareProject"
      />
    </v-col>
    <v-col v-show="sharings.length" cosl="12">
      <h3 class="text-subtitle">
        Partagé avec
      </h3>
      <v-list max-height="400px" class="overflow-auto">
        <v-list-item v-for="share in sharings" :key="share.id">
          {{ share.user_email }}
        </v-list-item>
      </v-list>
    </v-col>
  </v-row>
</template>

<script>
import { mdiShare } from '@mdi/js'

export default {
  props: {
    project: {
      type: Object,
      required: true
    }
  },
  data () {
    return {
      icons: {
        mdiShare
      },
      emailsInput: '',
      sharings: []
    }
  },
  async mounted () {
    const { data: sharings, error } = await this.$supabase.from('projectsSharing').select('*').eq('project_id', this.project.id)

    if (!error) {
      this.sharings = sharings
    } else {
      // eslint-disable-next-line no-console
      console.log(error)
    }
  },
  methods: {
    async shareProject () {
      const newSharings = this.emailsInput.split(',').map((email) => {
        return {
          user_email: email.toLowerCase().trim(),
          project_id: this.project.id,
          shared_by: this.$user.id
        }
      })

      await this.$supabase.from('projectsSharing').insert(newSharings)

      this.sharings.push(...newSharings)
      this.emailsInput = ''
    }
  }
}
</script>
