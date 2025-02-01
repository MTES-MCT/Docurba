
<template>
  <v-dialog v-model="dialog" width="800">
    <template #activator="{ on, attrs }">
      <v-list-item link v-bind="attrs" v-on="on">
        <v-list-item-title>
          Volet qualitatif
        </v-list-item-title>
      </v-list-item>
    </template>

    <v-card>
      <v-card-title class="text-h5 d-flex flex-column">
        <div>Volet qualitatif</div>
      </v-card-title>

      <v-card-text class="pt-4">
        <v-container>
          <template v-if="voletQualitatif">
            <v-row class="white">
              <v-col cols="12">
                <v-row v-for="(vq, i) in voletQualitatif" :key="'vq_' + i">
                  <v-col v-if="vq.header" cols="12" class="mention-grey--text">
                    {{ vq.title }}
                  </v-col>
                  <template v-else>
                    <v-col cols="12">
                      <div>
                        <div class="typo--text">
                          {{ vq.title }} : <span class="font-weight-bold ">{{ formatVal(vq.value) }}</span>
                        </div>
                      </div>
                    </v-col>
                  </template>
                </v-row>
              </v-col>
            </v-row>
          </template>
        </v-container>
      </v-card-text>
    </v-card>
  </v-dialog>
</template>
<script>
import { mdiDotsVertical } from '@mdi/js'

export default
{
  name: 'VoletQualiDialog',
  props: {},
  data () {
    return {
      dialog: false,
      voletQualitatifRaw: null,
      icons: {
        mdiDotsVertical
      }
    }
  },
  computed: {
    voletQualitatif () {
      if (this.voletQualitatifRaw) {
        const details = this.voletQualitatifRaw
        return [
          { title: 'Évaluation environnementale', value: details.vq_sievaluationenvironement, hint: 'siEvaluationEnvironement - Evaluation environnementale' },
          { title: 'Disposition d’aménagement des OAP', header: true },
          { title: 'Environnement', value: details.vq_sievaluationenvironnementale, hint: 'siEvaluationEnvironnementale - Evaluation environnementale' },
          { title: 'Paysage', value: !!details.is_paysage, hint: 'siPysage - Paysage' },
          { title: 'Entrée en ville', value: !!details.is_entree_ville, hint: 'siEntreeville - Entrée de ville' },
          { title: 'Patrimoine', value: !!details.is_patrimoine, hint: 'siPatrimoine - Patrimoine' },
          { title: 'Lutte contre l\'insalubrité', value: !!details.is_lutte_insalubrite, hint: 'siLutteInsaLubrite - Lutte contre l\'insalubrité' },
          { title: 'Renouvellement urbain', value: !!details.is_renouvel_urbain, hint: 'siRenouvellementUrbain - Renouvellement urbain' },
          { title: 'Développement', value: !!details.is_developpement, hint: 'siDeveloppement - Développement' },
          { title: 'Mixité fonctionnelle:', value: !!details.is_developpement, hint: 'Mixité fonctionnelle:' },
          { title: 'Mixité fonctionnelle:', value: !!details.is_developpement, hint: 'Mixité fonctionnelle:' },
          { title: 'Échéancier d’ouverture à l’urbanisation:', value: !!details.vq_sisecteuramenagementsansreglement, hint: 'Échéancier d’ouverture à l’urbanisation:- Schémas d\'aménagement sans réglèment' }, // NO IN SCHEMA,
          { title: 'Schémas d’aménagement:', value: !!details.vq_sisecteuramenagementsansreglement, hint: 'Schémas d’aménagement' }, // NO IN SCHEMA,
          { title: 'Adaptation du périmètre de plafonnement du stationnement:', value: !!details.vq_sisecteuramenagementsansreglement, hint: 'Schémas d’aménagement' }, // NO IN SCHEMA,
          { title: 'Schémas d’aménagement sans règlement:', value: !!details.vq_sisecteuramenagementsansreglement, hint: 'Schémas d’aménagement' }, // NO IN SCHEMA,
          { title: 'Adaptation au recul du trait de côté::', value: !!details.vq_sisecteuramenagementsansreglement, hint: 'Schémas d’aménagement' }, // NO IN SCHEMA,
          { title: 'Trajectoire ZAN:', value: !!details.vq_sisecteuramenagementsansreglement, hint: 'Schémas d’aménagement' }, // NO IN SCHEMA,
          { title: 'ENR:', value: !!details.vq_sisecteuramenagementsansreglement, hint: 'Schémas d’aménagement' }, // NO IN SCHEMA,
          { title: 'Règlement', header: true },
          { title: 'sistecal', value: !!details.vq_sistecal, hint: 'sistecal --' }, // NO IN SCHEMA
          { title: 'nombrestecal', value: details.vq_nombrestecal, hint: 'nombrestecal' }, // NO IN SCHEMA
          { title: 'sidensitemin', value: !!details.vq_sidensitemin, hint: 'sidensitemin' }, // NO IN SCHEMA
          { title: 'sinombremaxstationnement', value: !!details.vq_sinombremaxstationnement, hint: 'sinombremaxstationnement - nombre maximale d\'aires de stationnement' }, // NO IN SCHEMA
          { title: 'siprescriptioncomelec', value: !!details.vq_siprescriptioncomelec, hint: 'Prescriptions pour communications électroniques' }, // NO IN SCHEMA
          { title: 'sirenvoirnu', value: !!details.vq_sirenvoirnu, hint: 'sirenvoirnu - si renvoi au RNU' }, // NO IN SCHEMA
          { title: 'siobligationrealstationnement', value: !!details.vq_siobligationrealstationnement, hint: 'siobligationrealstationnement - Obligation de réalisation d\'aires de stationnement' } // NO IN SCHEMA
        ]
      }
      return []
    }
  },
  async mounted () {
    const { data: procedure, error: errorProcedure } = await this.$supabase.from('procedures')
      .select('*')
      .eq('id', this.$route.params.procedureId)
    if (errorProcedure) { throw errorProcedure }
    this.voletQualitatifRaw = procedure[0].volet_qualitatif
  },
  methods: {
    formatVal (val) {
      if (typeof val === 'boolean') {
        return val ? 'Oui' : 'Non'
      }
      return val
    }

  }
}
</script>
