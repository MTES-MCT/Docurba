<template>
  <v-row justify="center">
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
        <v-hover v-for="sharing in sharings" v-slot="{hover}" :key="sharing.id">
          <v-list-item>
            <v-list-item-content>
              <v-list-item-title> {{ sharing.user_email }}</v-list-item-title>
            </v-list-item-content>
            <v-list-item-action>
              <v-select
                v-model="sharing.role"
                hide-details
                dense
                filled
                class="role-select"
                :items="roles"
                @change="updateRole(sharing)"
              />
            </v-list-item-action>
            <v-list-item-action class="my-0">
              <v-btn v-show="hover" small icon @click="cancelSharing(sharing.user_email)">
                <v-icon>{{ icons.mdiCloseCircleOutline }}</v-icon>
              </v-btn>
            </v-list-item-action>
          </v-list-item>
        </v-hover>
      </v-list>
    </v-col>
  </v-row>
</template>

<script>
import { mdiShare, mdiCloseCircleOutline } from '@mdi/js'
import axios from 'axios'

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
        mdiShare,
        mdiCloseCircleOutline
      },
      roles: [{
        text: 'Lecture',
        value: 'read'
      }, {
        text: 'Edition',
        value: 'write'
      }],
      emailsInput: '',
      sharings: []
    }
  },
  watch: {
    'project.id' () {
      this.getSharings()
    }
  },
  mounted () {
    this.getSharings()
  },
  methods: {
    async getSharings () {
      this.sharings = []
      const { data: sharings, error } = await this.$supabase.from('projects_sharing').select('*').eq('project_id', this.project.id)

      if (!error) {
        this.sharings = sharings
      } else {
        // eslint-disable-next-line no-console
        console.log(error)
      }
    },
    async cancelSharing (email) {
      this.sharings = this.sharings.filter(s => s.user_email !== email)
      await this.$supabase.from('projects_sharing').delete().match({
        user_email: email,
        project_id: this.project.id
      })
    },
    async shareProject () {
      const newSharings = this.emailsInput.split(',').map((email) => {
        return {
          user_email: email.toLowerCase().trim(),
          project_id: this.project.id,
          shared_by: this.$user.id
        }
      })

      await this.$supabase.from('projects_sharing').insert(newSharings)

      axios({
        url: '/api/projects/notify/shared',
        method: 'post',
        data: {
          sharings: newSharings
        }
      })

      this.sharings.push(...newSharings)
      this.emailsInput = ''
    },
    async updateRole (sharing) {
      const { data: updatedSharing, error } = await this.$supabase.from('projects_sharing').update({
        role: sharing.role
      }).eq('id', sharing.id)

      if (!error) {
        // TODO: Add a feedback here that the change is good.

        // eslint-disable-next-line no-console
        console.log(updatedSharing)
      } else {
        // eslint-disable-next-line no-console
        console.log(error)
      }
    }
  }
}
</script>
<style scoped>
.role-select {
  max-width: 150px;
}
</style>
