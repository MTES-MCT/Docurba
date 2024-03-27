<template>
  <div>
    <slot>
      <div class="primary--text" style="font-weight: 500; cursor:pointer;" @click.stop="dialog = true">
        {{ perimetre?.length }} communes
      </div>
    </slot>
    <v-dialog
      v-model="dialog"
      width="800"
    >
      <v-container class="pa-10 white">
        <v-row>
          <v-col cols="12" class="pt-0 pb-8 d-flex justify-end">
            <div style="font-weight: 500; cursor:pointer;" class=" primary--text" @click="dialog = false">
              Fermer x
            </div>
          </v-col>
        </v-row>
        <v-row>
          <v-col cols="12">
            <div class="text-h5 font-weight-bold mb-4">
              Périmètre de {{ docName }}
            </div>
          </v-col>
        </v-row>
        <v-row>
          <v-col cols="12">
            <div>
              <div class="mention-grey--text mb-3">
                {{ perimetre?.length }} communes:
              </div>
              <div v-if="fullPerimetre">
                <div v-for="(town, i) in fullPerimetre" :key="`perimetre_${town.code}-${i}`" class="mr-6 pb-4 d-inline-block">
                  <nuxt-link class="font-weight-bold text-decoration-none" :to="`/ddt/${town.departementCode}/collectivites/${town.code}/${town.code.length > 5 ? 'epci' : 'commune'}`">
                    {{ town.intitule }}   ({{ town.code }})
                  </nuxt-link>
                </div>
              </div>
            </div>
          </v-col>
        </v-row>
        <v-row>
          <v-col cols="12" class="mt-2">
            <v-btn
              color="primary"

              @click="dialog = false"
            >
              Fermer
            </v-btn>
          </v-col>
        </v-row>
      </v-container>
    </v-dialog>
  </div>
</template>

<script>
export default {
  props: {
    perimetre: {
      type: Array,
      required: true
    },
    docName: {
      type: String,
      required: true
    }
  },
  data () {
    return {
      dialog: false,
      fullPerimetre: null
    }
  },
  watch: {
    async dialog (newVal) {
      if (newVal) {
        const rawReferentiel = await fetch(`/api/geo/collectivites?codes=${this.perimetre.map(e => e.collectivite_code)}`)
        const referentiel = await rawReferentiel.json()
        this.fullPerimetre = referentiel.filter(e => this.perimetre.map(y => y.collectivite_code).includes(e.code))
      }
    }
  }
}
</script>
