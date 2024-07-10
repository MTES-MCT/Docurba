
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
                  <v-col cols="6">
                    <div class="justify-text-end">
                      <div class="font-weight-bold d-flex justify-end">
                        {{ vq.title }} :
                      </div>
                    </div>
                  </v-col>
                  <v-col cols="6">
                    <div>
                      {{ vq.value }}
                      <v-tooltip bottom>
                        <template #activator="{ on, attrs }">
                          <v-icon
                            color="primary"
                            class="ml-1"
                            dark
                            v-bind="attrs"
                            v-on="on"
                          >
                            {{ icons.mdiInformationOutline }}
                          </v-icon>
                        </template>
                        <span>{{ vq.hint }}</span>
                      </v-tooltip>
                    </div>
                  </v-col>
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
          { title: 'siEvaluationEnvironement', value: details.vq_sievaluationenvironement, hint: 'siEvaluationEnvironement - Evaluation environnementale' },
          { title: 'siDocAmmenagmentComm', value: !!details.vq_sidocammenagmentcomm, hint: 'siDocAmmenagmentComm - Document d\'aménagement commerciale' },
          { title: 'siIntegrationDispoLoiENE', value: !!details.vq_siintegrationdispoloiene, hint: 'siIntegrationDispoLoiENE - Intégration des dispositions de la loi ENE' },
          { title: 'siEvaluationEnvironnementale', value: details.vq_sievaluationenvironnementale, hint: 'siEvaluationEnvironnementale - Evaluation environnementale' },
          { title: 'siScotAvecDAC', value: !!details.vq_siscotavecdac, hint: 'siScotAvecDAC - Le SCOT comporte un DAC' },
          { title: 'siLoiLME', value: !!details.vq_siloilme, hint: 'siLoiLME - Fondement juridique' },
          { title: 'siLoiENE', value: !!details.vq_siloiene, hint: 'siLoiENE - Fondement juridique' },
          { title: 'siEspaceNaturels', value: !!details.vq_siespacenaturels, hint: 'siEspaceNaturels - Espaces naturels' },
          { title: 'siEspaceAgricoles', value: !!details.vq_siespaceagricoles, hint: 'siEspaceAgricoles - Espaces agricoles' },
          { title: 'siEspaceUrbains', value: !!details.vq_siespaceurbains, hint: 'siEspaceUrbains - Espaces urbains' },
          { title: 'siSchemasSecteur', value: !!details.vq_sischemassecteur, hint: 'siSchemasSecteur - Schémas de secteur' },
          { title: 'siChapitreValantSMVM', value: !!details.vq_sichapitrevalantsmvm, hint: 'siChapitreValantSMVM - Chapitre individualisé valant SMVM' },
          { title: 'siCompatibiliteLittoral', value: !!details.vq_sicompatibilitelittoral, hint: 'siCompatibiliteLittoral - Compatibilité Loi Littoral' },
          { title: 'siCompatibiliteMontagne', value: !!details.vq_sicompatibilitemontagne, hint: 'siCompatibiliteMontagne - Compatibilité Loi Montagne' },
          { title: 'siCompatibiliteSDAGE', value: !!details.vq_sicompatibilitesdage, hint: 'siCompatibiliteSDAGE - Compatibilité SDAGE' },
          { title: 'siCompatibilitePGRI', value: !!details.vq_sicompatibilitepgri, hint: 'siCompatibilitePGRI - Compatibilité PGRI' },
          { title: 'siCompatibiliteParcsNaturels', value: !!details.vq_sicompatibiliteparcsnaturels, hint: 'siCompatibiliteParcsNaturels - Compatibilité Charte Parcs Naturels' },
          { title: 'siPriseEnCptSRCE', value: !!details.vq_sipriseencptsrce, hint: 'siPriseEnCptSRCE - Prise en compte SRCE' },
          { title: 'siPriseEnCptPCET', value: !!details.vq_sipriseencptpcet, hint: 'siPriseEnCptPCET - Prise en compte PCET' },
          { title: 'simixitesociale', value: !!details.vq_simixitesociale, hint: 'simixitesociale - mixité sociale' }, // NO IN SCHEMA
          { title: 'sisecteuramenagementsansreglement', value: !!details.vq_sisecteuramenagementsansreglement, hint: 'sisecteuramenagementsansreglement- Schémas d\'aménagement sans réglèment' }, // NO IN SCHEMA,
          { title: 'siadaptationplafonstationnemt', value: !!details.vq_siadaptationplafonstationnemt, hint: 'siadaptationplafonstationnemt - Adaptation du périmètre de plafonnement du stationnement' }, // NO IN SCHEMA
          { title: 'sistecal', value: !!details.vq_sistecal, hint: 'sistecal --' }, // NO IN SCHEMA
          { title: 'nombrestecal', value: details.vq_nombrestecal, hint: 'nombrestecal' }, // NO IN SCHEMA
          { title: 'sidensitemin', value: !!details.vq_sidensitemin, hint: 'sidensitemin' }, // NO IN SCHEMA
          { title: 'sinombremaxstationnement', value: !!details.vq_sinombremaxstationnement, hint: 'sinombremaxstationnement - nombre maximale d\'aires de stationnement' }, // NO IN SCHEMA
          { title: 'siprescriptioncomelec', value: !!details.vq_siprescriptioncomelec, hint: 'Prescriptions pour communications électroniques' }, // NO IN SCHEMA
          { title: 'sirenvoirnu', value: !!details.vq_sirenvoirnu, hint: 'sirenvoirnu - si renvoi au RNU' }, // NO IN SCHEMA
          { title: 'siobligationrealstationnement', value: !!details.vq_siobligationrealstationnement, hint: 'siobligationrealstationnement - Obligation de réalisation d\'aires de stationnement' }, // NO IN SCHEMA
          { title: 'sietudeidentespaces', value: !!details.vq_sietudeidentespaces, hint: 'sietudeidentespaces - Etude d\'identification des espaces à définir' }, // NO IN SCHEMA
          { title: 'concerneloilittoral', value: details.vq_concerneloilittoral, hint: 'concerneloilittoral- Concerné par la loi Littoral' } // NO IN SCHEMA
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

  }
}
</script>
