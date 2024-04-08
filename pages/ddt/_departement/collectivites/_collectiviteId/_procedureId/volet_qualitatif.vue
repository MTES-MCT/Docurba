<template>
  <v-container>
    <v-row>
      <v-col cols="12">
        <div class="text-h1">
          Volet qualitatif
        </div>
      </v-col>
      <v-col cols="12">
        <div class="d-flex">
          <!-- <nuxt-link
            :to="{ name: `ddt-departement-collectivites-collectiviteId-${$sudocu.isEpci($route.params.collectiviteId) ? 'epci' : 'commune'}`, params: { departement: $route.params.departement, collectiviteId: $route.params.collectiviteId }}"
          >
            <v-icon small color="primary" class="mr-2">
              {{ icons.mdiArrowLeft }}
            </v-icon>
            <span>Revenir à mon tableau de bord</span>
          </nuxt-link> -->
        </div>
      </v-col>
    </v-row>
    <DashboardDdtInfosTabs />

    <v-row>
      <v-col cols="12 pl-0 mb-4">
        <div class="text-h2 mt-8">
          Volet qualitatif
        </div>
      </v-col>
    </v-row>
    <v-row class="white-bordered-card pa-8 mb-4">
      <v-col v-if="rawDetails" cols="12">
        <div>
          <div class="font-weight-bold ">
            Evaluation environnementale : {{ rawDetails.eval_environmental }}
          </div>
        </div>
      </v-col>
      <!-- <v-col v-if="rawDetails" cols="6">
        <div>
          {{ rawDetails[0].vq_sievaluationenvironnementale }}
        </div>
      </v-col> -->
    </v-row>

    <v-row>
      <v-col cols="12" class=" pl-0 mb-4">
        <div class="text-h2">
          Loi ENE
        </div>
      </v-col>
    </v-row>
    <template v-if="loienes">
      <v-row class="white-bordered-card  pa-8 ">
        <v-col cols="12">
          <v-row>
            <v-col cols="12" class="text-h5 font-weight-bold">
              Disposition d’aménagement des OAP
            </v-col>
          </v-row>
          <v-row v-for="(oap, i) in loienes.oaps" :key="'le_' + i">
            <v-col cols="6">
              <div class="justify-text-end">
                <div class="font-weight-bold d-flex justify-end">
                  {{ oap.title }} :
                </div>
              </div>
            </v-col>
            <v-col cols="6">
              <div>
                <v-chip v-if="typeof oap.value === 'boolean'" :color="oap.value ? 'success' : 'error'" small label class="text-uppercase mr-2">
                  {{ oap.value ? 'Oui' : 'Non' }}
                </v-chip>
                <div v-else>
                  {{ oap.value }}
                </div>

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
                  <span>{{ oap.hint }}</span>
                </v-tooltip>
              </div>
            </v-col>
          </v-row>
        </v-col>
      </v-row>
      <v-row class="white-bordered-card pa-8 mt-12">
        <v-col cols="12">
          <v-row>
            <v-col cols="12" class="text-h5 font-weight-bold">
              Règlement
            </v-col>
          </v-row>
          <v-row v-for="(reglement, i) in loienes.reglements" :key="'le_' + i">
            <v-col cols="6">
              <div class="justify-text-end">
                <div class="font-weight-bold d-flex justify-end">
                  {{ reglement.title }} :
                </div>
              </div>
            </v-col>
            <v-col cols="6">
              <div>
                <v-chip v-if="typeof reglement.value === 'boolean'" :color="reglement.value ? 'success' : 'error'" small label class="text-uppercase mr-2">
                  {{ reglement.value ? 'Oui' : 'Non' }}
                </v-chip>
                <span v-else>
                  {{ reglement.value }}
                </span>

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
                  <span>{{ reglement.hint }}</span>
                </v-tooltip>
              </div>
            </v-col>
          </v-row>
        </v-col>
      </v-row>
      <v-row class="white-bordered-card pa-8  my-12">
        <v-col cols="12">
          <v-row>
            <v-col cols="12" class="text-h5 font-weight-bold">
              Commentaire
            </v-col>
          </v-row>
          <v-row v-if="loienes.commentaire">
            <v-col cols="12">
              <div v-if="loienes.commentaire.value">
                {{ loienes.commentaire.value }}
              </div>
              <div v-else class="text--disabled">
                Pas de commentaire
              </div>
            </v-col>
          </v-row>
        </v-col>
      </v-row>
    </template>
    <v-row v-else>
      <v-col cols="12">
        <VGlobalLoader />
      </v-col>
    </v-row>

    <!-- <v-row class="white">
      <v-col cols="12">
        <div class="text-h2">
          Table Volet Qualitatif
        </div>
      </v-col>
    </v-row>
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
    <v-row v-else>
      <v-col cols="12">
        <VGlobalLoader />
      </v-col>
    </v-row> -->
  </v-container>
</template>

<script>
import { mdiInformationOutline } from '@mdi/js'

export default {
  name: 'InformationsGenerales',
  layout: 'ddt',
  data () {
    return {
      icons: {
        mdiInformationOutline
      },
      rawDetails: null

    }
  },
  computed: {
    voletQualitatif () {
      if (this.rawDetails) {
        const details = this.rawDetails
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
    },
    loienes () {
      if (this.rawDetails) {
        const details = this.rawDetails
        return {
          oaps: [
            { title: 'Environnement', value: !!details.is_environnement, hint: 'siEnvironnement - Environnement' },
            { title: 'Paysage', value: !!details.is_paysage, hint: 'siPysage - Paysage' },
            { title: 'Entrée en ville', value: !!details.is_entree_ville, hint: 'siEntreeville - Entrée de ville' },
            { title: 'Patrimoine', value: !!details.is_patrimoine, hint: 'siPatrimoine - Patrimoine' },
            { title: 'Lutte contre l\'insalubrité', value: !!details.is_lutte_insalubrite, hint: 'siLutteInsaLubrite - Lutte contre l\'insalubrité' },
            { title: 'Renouvellement urbain', value: !!details.is_renouvel_urbain, hint: 'siRenouvellementUrbain - Renouvellement urbain' },
            { title: 'Développement', value: !!details.is_developpement, hint: 'siDeveloppement - Développement' },
            // MIXITE FONCITONNELLE
            { title: 'Échéancier d’ouverture à l’urbanisation', value: !!details.is_ouverture_urbain, hint: 'siEcheancierOuvertureUrba - Echéancier d\'ouverture à l\'urbanisation' }
          // Adaptation du périmètre de plafonnement du stationnement
          ],
          reglements: [
            // STECAL
          // Nb STECAL
            { title: 'STECAL', value: !!details.is_stecal, hint: 'sistecal --' }, // NO IN SCHEMA
            { title: 'Nombre de STECAL', value: details.nb_stecal ?? '0', hint: 'nombrestecal' }, // NO IN SCHEMA

            { title: 'Densité minimale', value: !!details.is_densite_mini, hint: 'siDensiteMin - Densité minimale' },
            { title: 'Nombre maximal d’aires de stationnement', value: !!details.le_sinbrmaxairestationnement, hint: 'siNbrMaxAireStationnement - Nombre maximal d\'aires de stationnement' },
            // Prescriptions pour communications électroniques
            // RNU
            { title: 'Obligation de réalisation d’aires de stationnement', value: !!details.is_obligation_aire_statmnt, hint: 'siObligationStationnement - Obligation (minimale ou maximale) d\'aire de stationnement' }
          ]
          // commentaire: { title: 'commentaire', value: details.le_commentaire, hint: 'commentaire - Commentaire' }
        }
        // return [
        //   { title: 'Environnement', value: !!details.le_sienvironnement, hint: 'siEnvironnement - Environnement' },
        //   { title: 'Paysage', value: !!details.le_sipaysage, hint: 'siPysage - Paysage' },
        //   { title: 'Entrée en ville', value: !!details.le_sientreeville, hint: 'siEntreeville - Entrée de ville' },
        //   { title: 'Patrimoine', value: !!details.le_sipatrimoine, hint: 'siPatrimoine - Patrimoine' },
        //   { title: 'Lutte contre l\'insalubrité', value: !!details.le_silutteinsalubrite, hint: 'siLutteInsaLubrite - Lutte contre l\'insalubrité' },
        //   { title: 'Renouvellement urbain', value: !!details.le_sirenouvellementurbain, hint: 'siRenouvellementUrbain - Renouvellement urbain' },
        //   { title: 'Développement', value: !!details.le_sideveloppement, hint: 'siDeveloppement - Développement' },
        //   // MIXITE FONCITONNELLE
        //   { title: 'Échéancier d’ouverture à l’urbanisation', value: !!details.le_siecheancierouvertureurba, hint: 'siEcheancierOuvertureUrba - Echéancier d\'ouverture à l\'urbanisation' },
        //   // Adaptation du périmètre de plafonnement du stationnement

        //   // Reglement
        //   // STECAL
        //   // Nb STECAL
        //   { title: 'Densité minimale', value: !!details.le_sidensitemin, hint: 'siDensiteMin - Densité minimale' },
        //   { title: 'Nombre maximal d’aires de stationnement', value: !!details.le_sinbrmaxairestationnement, hint: 'siNbrMaxAireStationnement - Nombre maximal d\'aires de stationnement' },
        //   // Prescriptions pour communications électroniques
        //   // RNU
        //   { title: 'Obligation de réalisation d’aires de stationnement', value: !!details.le_siobligationstationnement, hint: 'siObligationStationnement - Obligation (minimale ou maximale) d\'aire de stationnement' },

        //   { title: 'Plan de secteur', value: !!details.le_siplansecteur, hint: 'siPlanSecteur - Plan de secteur' },
        //   { title: 'siSecteurProjet', value: !!details.le_sisecteurprojet, hint: 'siSecteurProjet - Secteur de projets' },
        //   { title: 'siSchemasAmenagements', value: !!details.le_sischemasamenagements, hint: 'siSchemasAmenagements - Schémas d\'aménagement' },
        //   { title: 'siZonesNaturelles', value: !!details.le_sizonesnaturelles, hint: 'siZonesNaturelles - Zones naturelles' },
        //   { title: 'siZonesAgricoles', value: !!details.le_sizonesagricoles, hint: 'siZonesAgricoles - Zones agricoles' },
        //   { title: 'siPrescriptions', value: !!details.le_siprescriptions, hint: 'siPrescriptions - Prescriptions' },
        //   { title: 'siObjConsoEspaceParSecteur', value: !!details.le_siobjconsoespaceparsecteur, hint: 'siObjConsoEspaceParSecteur - Objectifs de consommation d\'espace par secteur' },
        //   { title: 'siUtilisationTerrainAvantUrba', value: !!details.le_siutilisationterrainavanturba, hint: 'siUtilisationTerrainAvantUrba - Utilisation de terrains équipés avant urbanisation nouvelle' },
        //   { title: 'siEtudeImpacteUrbanisation', value: !!details.le_sietudeimpacteurbanisation, hint: 'siEtudeImpacteUrbanisation - Etude d\'impact préalable à l\'urbanisation' },
        //   { title: 'siEtudeDensification', value: !!details.le_sietudedensification, hint: 'siEtudeDensification - Etude de densification' },
        //   { title: 'siSecteurDensiteMin', value: !!details.le_sisecteurdensitemin, hint: 'siSecteurDensiteMin - Secteurs à densité minimale de construction à proximitée des TC' },
        //   { title: 'siObligationPluStationnement', value: !!details.le_siobligationplustationnement, hint: 'siObligationPluStationnement - Obligation pour PLU d\'aires de stationnement de véhicules non motorisés' },
        //   { title: 'siSecteurEnergieEnvironnement', value: !!details.le_sisecteurenergieenvironnement, hint: 'siSecteurEnergieEnvironnement - Secteurs à performances énergétiques et environnementales renforcées' },
        //   { title: 'siSecteurCommunicationElectro', value: !!details.le_sisecteurcommunicationelectro, hint: 'siSecteurCommunicationElectro - Secteurs à qualité de communications électroniques renforcées' },
        //   { title: 'siSecteurAvecNorme', value: !!details.le_sisecteuravecnorme, hint: 'siSecteurAvecNorme - Secteurs avec normes de qualité urbaine, architecturale et paysagère' },
        //   { title: 'siEspaceVert', value: !!details.le_siespacevert, hint: 'siEspaceVert - Maintien ou création d\'espaces verts' },
        //   { title: 'siModaliteRepartitionLogementEpci', value: !!details.le_simodaliterepartitionlogementepci, hint: 'siModaliteRepartitionLogementEpci - Modalité de répartition des nouveaux logements' },
        //   { title: 'siModaliteRepartitionlogementCommune', value: !!details.le_simodaliterepartitionlogementcommune, hint: 'siModaliteRepartitionlogementCommune - Modalité de répartition des nouveaux logements' },
        //   { title: 'siObjectifAmeliorationParc', value: !!details.le_siobjectifameliorationparc, hint: 'siObjectifAmeliorationParc - Objectifs d\'amélioration du parc existant' },
        //   { title: 'siPublicationAnalyse', value: !!details.le_sipublicationanalyse, hint: 'siPublicationAnalyse - Publication de l\'analyse à ans' },
        //   { title: 'dateVoletQualitatif', value: details.le_datevoletqualitatif, hint: 'dateVoletQualitatif - Date volet qualitatif' }, // DATE TYPE A CHANGER
        //   { title: 'commentaire', value: details.le_commentaire, hint: 'commentaire - Commentaire' } // TEXTE
        // ]
      }
      return []
    }
  },
  async mounted () {
    const { data: procedure, error: errorProcedure } = await this.$supabase.from('procedures')
      .select('*')
      .eq('id', this.$route.params.procedureId)
    if (errorProcedure) { throw errorProcedure }
    this.rawDetails = procedure[0].volet_qualitatif
  }
}
</script>

<style lang="scss">
.white-bordered-card{
  border: solid 1px var(--v-primary-lighten1) !important;
  background: white;
  border-radius: 4px;
}
</style>
