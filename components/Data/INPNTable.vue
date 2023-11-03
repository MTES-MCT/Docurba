<template>
  <v-data-table
    :headers="headers"
    :items="communesItems"
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
        <v-btn
          v-if="selectable"
          color="primary"
          fab
          x-small
          @click="select(item)"
        >
          <v-icon>{{ isSelected(item) ? icons.mdiCheck : icons.mdiPlus }}</v-icon>
        </v-btn>
      </div>
    </template>
  </v-data-table>
</template>

<script>
import { mdiLink, mdiPlus, mdiCheck } from '@mdi/js'

export default {
  props: {
    communes: {
      type: Array,
      required: true
    },
    selectable: {
      type: Boolean,
      default: false
    },
    selection: {
      type: Array,
      default: () => []
    }
  },
  data () {
    return {
      icons: {
        mdiLink,
        mdiPlus,
        mdiCheck
      },
      headers: [
        {
          text: 'Commune',
          value: 'intitule'
        },
        { text: 'Liens', value: 'actions', sortable: false, align: 'center' }
      ]
    }
  },
  computed: {
    communesItems () {
      return this.communes.map((e) => {
        const urlInpn = `https://inpn.mnhn.fr/collTerr/commune/${e.code}`
        const enriched = {
          ...e,
          url: `https://inpn.mnhn.fr/collTerr/biodiversity/INSEEC${e.code}`,
          urlEspaces: `${urlInpn}/tab/espaces`,
          urlZnieff: `${urlInpn}/tab/znieff`,
          urlInpg: `${urlInpn}/tab/inpg`,
          urlNatura2000: `${urlInpn}/tab/natura2000`,
          urlArcheo: `${urlInpn}/tab/archeo`
        }
        return enriched
      })
    }
  },
  methods: {
    select (item) {
      if (this.isSelected(item)) {
        this.$emit('remove', item.url)
      } else {
        this.$emit('add', {
          title: item.intitule,
          category: null,
          source: 'INPN',
          url: item.url,
          links: null,
          extra: null
        })
      }
    },
    isSelected (item) {
      return !!this.selection.find(attachment => item.url === attachment.url)
    }
  }
}
</script>
