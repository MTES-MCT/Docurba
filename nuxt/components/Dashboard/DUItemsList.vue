<template>
  <v-row>
    <v-col v-if="procedures.length > 0 || schemas.length > 0">
      <v-tabs
        v-model="tab"
        color="primary"
      >
        <v-tab>
          DU intercommunaux
        </v-tab>
        <v-tab>
          <span>DU communaux</span>
        </v-tab>
        <v-tab>
          SCoT
        </v-tab>
        <v-spacer />
        <v-btn v-if="!isPublic" depressed color="primary" class="align-self-center" :to="`/ddt/${collectivite.departementCode}/collectivites/${collectivite.code}/procedure/add`">
          Ajouter une procédure
        </v-btn>
      </v-tabs>

      <v-tabs-items v-model="tab" :class="{beige: !isPublic}">
        <v-tab-item>
          <template v-if="DUInter.length > 0">
            <DashboardDUItem
              v-for="(procedure,i) in DUInter"
              :key="'du_' + i"
              :procedure="procedure"
              :censored="isPublic"
              :collectivite="collectivite"
              @delete="$emit('deleteProcedure', arguments[0])"
            />
          </template>
          <div v-else class="d-flex align-center justify-center pa-8 text--disabled flex-column g200  rounded">
            <p>
              Il n'y a pas de DU intercommunaux
            </p>
            <p class="font-weight-bold">Cliquez sur l'onglet suivant pour afficher les DU communaux.</p>
          </div>
        </v-tab-item>
        <v-tab-item>
          <template v-if="DUCommunaux.length > 0">
            <DashboardDUItem
              v-for="(procedure,i) in DUCommunaux"
              :key="'du_' + i"
              :procedure="procedure"
              :censored="isPublic"
              :collectivite="collectivite"
              @delete="$emit('deleteProcedure', arguments[0])"
            />
          </template>
          <div v-else class="d-flex align-center justify-center pa-8 text--disabled flex-column g200  rounded">
            <p class="text-h1 mb-7">
              :'(
            </p>
            <p class="font-weight-bold">
              Pas de documents en compétence communal
            </p>
            <span class="font-italic">Astuce: Si vous ne voyez pas le document d'urbanisme recherché, vérifiez sur la commune ou l'EPCI qui a la compétence.</span>
          </div>
        </v-tab-item>
        <v-tab-item>
          <DashboardDUItem
            v-for="(procedure,i) in schemas"
            :key="'du_' + i"
            :procedure="procedure"
            :censored="isPublic"
            :collectivite="collectivite"
            @delete="$emit('deleteProcedure', arguments[0])"
          />
        </v-tab-item>
      </v-tabs-items>
    </v-col>
    <v-col v-else-if="isLoaded && procedures.length === 0" cols="12">
      <div class="text--secondary beige pa-6 mb-12 rounded">
        <div class="pb-6">
          Cette collectivité n'a pas de documents d'urbanisme sous sa compétence.
        </div>

        <v-btn v-if="!isPublic" color="primary" :to="`/ddt/${collectivite.departementCode}/collectivites/${collectivite.code}/procedure/add`">
          Ajouter une procédure
        </v-btn>
      </div>
    </v-col>
    <v-col v-else cols="12">
      <VGlobalLoader />
    </v-col>
  </v-row>
</template>

<script>
export default {
  name: 'DUItemsList',
  props: {
    collectivite: {
      type: Object,
      required: true
    },
    procedures: {
      type: Array,
      default () { return [] }
    },
    schemas: {
      type: Array,
      default: () => null
    },
    isPublic: {
      type: Boolean,
      default: false
    }
  },
  data () {
    return {
      tab: null,
      insertDialog: false
    }
  },
  computed: {
    isLoaded () {
      return !!this.procedures && !!this.collectivite
    },
    DUCommunaux () {
      return this.procedures?.filter(p => p.procedures_perimetres.length === 1)
    },
    DUInter () {
      return this.procedures?.filter(p => p.procedures_perimetres.length > 1)
    }
  }
}
</script>
