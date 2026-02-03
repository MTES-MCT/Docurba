<template>
  <v-dialog
    v-model="dialog"
    width="900"
  >
    <template #activator="{ on, attrs }">
      <span
        v-bind="attrs"
        class="primary--text text-decoration-underline mr-4"
        v-on="on"
      >
        Périmètre du document d'urbanisme ({{ perimetres.length }})
      </span>
    </template>

    <v-card>
      <v-card-title class="text-h5 primary white--text">
        Périmètre du document d'urbanisme ({{ perimetres.length }})
      </v-card-title>

      <v-card-text class="pb-0">
        <v-container class="py-8">
          <v-row v-if="infoBannerMessage || showHelp" class="align-center">
            <v-col v-if="infoBannerMessage" cols="8">
              <v-alert dense text type="info" class="mb-0">
                {{ infoBannerMessage }}
              </v-alert>
            </v-col>
            <v-col v-if="showHelp" cols="4">
              <SignalementProbleme />
            </v-col>
          </v-row>
          <v-row>
            <v-col
              v-for="collectivite in sortedCollectivites"
              :key="collectivite.code + collectivite.collectivite_type"
              cols="4"
              class="pl-0"
            >
              <nuxt-link :to="collectiviteLink(collectivite)">
                {{ collectivite.intitule }} ({{ collectivite.code }} {{ collectivite.collectivite_type }})
              </nuxt-link>
            </v-col>
          </v-row>
        </v-container>
      </v-card-text>

      <v-divider />

      <v-card-actions>
        <v-spacer />
        <v-btn
          color="primary"
          text
          @click="dialog = false"
        >
          Fermer
        </v-btn>
      </v-card-actions>
    </v-card>
  </v-dialog>
</template>

<script>
export default {
  props: {
    perimetres: {
      type: Array,
      required: true
    },
    infoBannerMessage: {
      type: String,
      default: '',
      required: false
    },
    showHelp: {
      type: Boolean,
      required: false
    }
  },
  data () {
    return {
      dialog: false
    }
  },
  computed: {
    sortedCollectivites () {
      return [...this.perimetres].sort((a, b) => a.intitule?.localeCompare(b.intitule))
    }
  },
  methods: {
    collectiviteLink (collectivite) {
      if (this.$user.profile.side === 'etat') {
        return `/ddt/${this.$route.params.departement}/collectivites/${collectivite.code}/commune`
      } else {
        return `/collectivites/${collectivite.code}`
      }
    }
  }
}
</script>
