<script>
import { mdiMagnify, mdiOpenInNew } from '@mdi/js'
import { displayDate } from '~/plugins/utils'

export default {
  data() {
    return {
      allVisible: false,
      icons: {
        mdiMagnify,
        mdiOpenInNew,
      },
      query: '',
    }
  },
  computed: {
    endDate() {
      return displayDate(this.$store.getters['survey/endDate'])
    },
    pagesCount() {
      // TODO :: Implement this
      return 5
    },
    query: {
      get() {
        return this.$route.query.r || ''
      },
      set(value) {
        this.$router.push({
          query: {
            ...this.$route.query,
            r: value || undefined,
          },
        })
      },
    },
    requiresValidationCount() {
      // TODO :: Implement this
      return 35
    },
    tabs() {
      return [{
        active: !this.$route.query.type,
        label: 'Procédures principales (hors SCoT)',
        to: {
          query: {
            ...this.$route.query,
            type: undefined,
          },
        },
      }, {
        active: this.$route.query.type === 'scot',
        label: 'SCoT',
        to: {
          query: {
            ...this.$route.query,
            type: 'scot',
          },
        },
      }]
    },
    year() {
      return this.$store.getters['survey/year']
    },
  },
}
</script>

<template>
  <FRGrid alt
          size="md lg-xl">
    <FRContainer>
      <FRGrid gap="lg-xs"
              highlighted>
        <FRContainer>
          <FRGrid gap="md lg-lg"
                  size="md lg-lg">
            <FRText h1
                    tag="h1">
              Enquête annuelle {{ year }}
            </FRText>
            <FRGrid gap="xs"
                    x-start>
              <FRText>
                L'enquête annuelle sur l'état d'avancement des documents d'urbanisme est disponible sur Docurba jusqu'au
                <strong>
                  {{ endDate }}
                </strong>
              </FRText>
              <FRLink :to="{ name: 'dsfr-docs-faq' }">
                Consignes et astuces dans notre FAQ
                <FRIcon :value="icons.mdiOpenInNew" />
              </FRLink>
            </FRGrid>
          </FRGrid>
        </FRContainer>
        <FRTabs :value="tabs">
          <FRGrid gap="md lg-xl">
            <div class="fr-row">
              <div class="fr-col fr-col-md-8">
                <FRField id="filter-all"
                         type="checkbox"
                         v-model="allVisible">
                  Afficher toutes les collectivités à valider ({{ requiresValidationCount }} restante{{ requiresValidationCount === 1 ? '' : 's' }})
                </FRField>
              </div>
              <div class="fr-col fr-col-md-4">
                <FRField :icon="icons.mdiMagnify"
                         id="filter-query"
                         placeholder="Rechercher une collectivité"
                         v-model="query" />
              </div>
            </div>
            <FRTable cols="5 2 5 3 3 3 3 9">
              <template #header>
                <FRTableCell>
                  Nom
                </FRTableCell>
                <FRTableCell>
                  Type
                </FRTableCell>
                <FRTableCell>
                  Procédures
                </FRTableCell>
                <FRTableCell>
                  Statut
                </FRTableCell>
                <FRTableCell>
                  Prescrit le
                </FRTableCell>
                <FRTableCell>
                  Approuvé le
                </FRTableCell>
                <FRTableCell>
                  Objet
                </FRTableCell>
                <FRTableCell>
                  <span>
                    Enquête {{ year }}
                  </span>
                  <FRButton sm
                            tertiary>
                    Valider toute la page
                  </FRButton>
                </FRTableCell>
              </template>
              <template #default></template>
            </FRTable>
            <FRPagination :value="pagesCount" />
          </FRGrid>
        </FRTabs>
      </FRGrid>
    </FRContainer>
  </FRGrid>
</template>
