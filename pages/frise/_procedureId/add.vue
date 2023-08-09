<template>
  <v-container>
    <v-row>
      <v-col cols="12">
        <v-btn text exact-path color="primary" nuxt :to="{name: 'frise-procedureId', params: { procedureId: $route.params.procedureId}}">
          <v-icon>{{ icons.mdiChevronLeft }}</v-icon> Revenir à la frise
        </v-btn>
      </v-col>
    </v-row>
    <v-row>
      <v-col cols="12">
        <h1 class="text-h1">
          Ajouter un événement
        </h1>
      </v-col>
      <FriseEventForm />
    </v-row>
  </v-container>
</template>

<script>
import { mdiChevronLeft } from '@mdi/js'

export default {
  name: 'AddTimelineEvent',
  layout ({ $user }) {
    if ($user?.profile?.poste === 'ddt' || $user?.profile?.poste === 'dreal') {
      return 'ddt'
    } else {
      return 'default'
    }
  },
  props: {
    projectId: {
      type: String,
      default () {
        return this.$route.params.projectId
      }
    }
  },
  data () {
    return {
      icons: {
        mdiChevronLeft
      }
    }
  },
  mounted () {
    this.$user.isReady.then(() => {
      if (this.$user?.profile?.poste === 'ddt' || this.$user?.profile?.poste === 'dreal') {
        this.$nuxt.setLayout('ddt')
      }
    })
  }
}
</script>
