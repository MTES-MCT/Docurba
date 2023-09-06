<template>
  <div>
    <v-container class="px-0">
      <v-row>
        <v-col cols="12">
          <h3>INPN pour {{ isEpci ? 'l\'Epci' : 'la commune' }} </h3>
        </v-col>
        <v-col cols="12">
          <p>
            Vous trouvez toutes les informations relatives à l'Inventaire National du Patrimoine Naturel surle site inpn.mnhn.fr.
          </p>
        </v-col>
      </v-row>
      <v-row v-if="communes">
        <v-col cols="12">
          <v-data-table
            :headers="headers"
            :items="communes"
            :items-per-page="10"
            :footer-props="{'items-per-page-text':'commune par page'}"
            class="elevation-1"
          >
            <template #[`footer.page-text`]="items">
              {{ items.pageStart }} - {{ items.pageStop }} de {{ items.itemsLength }}
            </template>

            <!-- eslint-disable-next-line -->
            <template #item.actions="{ item }">
              <div class="">
                <v-btn color="primary" text class="mr-4 my-2" target="_blank" :href="item.urlEspaces">
                  <v-icon
                    small
                    class="mr-2"
                  >
                    {{ icons.mdiLink }}
                  </v-icon>
                  Esp. protégés
                </v-btn>
                <v-btn color="primary" text class="mr-4 my-2" target="_blank" :href="item.urlZnieff">
                  <v-icon
                    small
                    class="mr-2"
                  >
                    {{ icons.mdiLink }}
                  </v-icon>
                  Znieff
                </v-btn>
                <v-btn color="primary" text class="mr-4 my-2" target="_blank" :href="item.urlInpg">
                  <v-icon
                    small
                    class="mr-2"
                  >
                    {{ icons.mdiLink }}
                  </v-icon>
                  INPG
                </v-btn>
                <v-btn color="primary" text class="mr-4 my-2" target="_blank" :href="item.urlNatura2000">
                  <v-icon
                    small
                    class="mr-2"
                  >
                    {{ icons.mdiLink }}
                  </v-icon>
                  Natura 2000
                </v-btn>
                <v-btn color="primary" text class="mr-4 my-2" target="_blank" :href="item.urlArcheo">
                  <v-icon
                    small
                    class="mr-2"
                    color="primary"
                  >
                    {{ icons.mdiLink }}
                  </v-icon>
                  Archéologiques
                </v-btn>
              </div>
            </template>
          </v-data-table>
        </v-col>
      </v-row>
      <v-row v-else>
        <VGlobalLoader />
      </v-row>
    </v-container>
  </div>
</template>

<script>
import { mdiLink } from '@mdi/js'

export default {
  name: 'Inpn',
  props: {
    isEpci: {
      type: Boolean,
      required: true
    },
    collectivite: {
      type: Object,
      required: true
    }
  },
  data () {
    return {
      icons: {
        mdiLink
      },
      headers: [
        {
          text: 'Commune',
          value: 'nom_commune'
        },
        { text: 'Liens', value: 'actions', sortable: false, align: 'center' }
      ],
      communes: null
    }
  },
  mounted () {
    // Start Analytics
    const inseeQuery = this.$route.query.insee
    const codes = typeof inseeQuery === 'object' ? inseeQuery : [inseeQuery]

    if (codes) {
      codes.forEach((code) => {
        this.$matomo([
          'trackEvent',
          'Socle de PAC',
          'Georisques',
          `${this.$route.query.document} - ${code}`
        ])
      })
    }
    // End Analytics

    let communesData
    if (this.isEpci) {
      communesData = this.collectivite.towns
    } else {
      communesData = [this.collectivite]
    }
    console.log('COMMUNE ID: ', communesData)
    communesData = communesData.map((e) => {
      const urlInpn = `https://inpn.mnhn.fr/collTerr/commune/${e.id || e.code_commune_INSEE}`
      const enriched = {
        ...e,
        urlEspaces: `${urlInpn}/tab/espaces`,
        urlZnieff: `${urlInpn}/tab/znieff`,
        urlInpg: `${urlInpn}/tab/inpg`,
        urlNatura2000: `${urlInpn}/tab/natura2000`,
        urlArcheo: `${urlInpn}/tab/archeo`
      }
      return enriched
    })
    this.communes = communesData
  }
}
</script>
