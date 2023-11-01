<template>
  <v-dialog v-model="dialog">
    <template #activator="{on}">
      <v-btn depressed tile icon v-on="on">
        <v-icon>{{ icons.mdiPaperclip }}</v-icon>
      </v-btn>
    </template>

    <v-card>
      <v-card-title>
        <span>Ajouter une donnée annexe à la section : {{ section.name }}</span>
        <v-spacer />
        <v-btn icon @click="dialog = false">
          <v-icon>{{ icons.mdiClose }}</v-icon>
        </v-btn>
      </v-card-title>

      <v-card-text>
        <v-tabs v-model="currentTab">
          <v-tab>Base territoriale</v-tab>
          <v-tab>Géorisques</v-tab>
          <v-tab>INPN</v-tab>
        </v-tabs>
        <v-tabs-items v-model="currentTab">
          <v-tab-item>
            <DataSourcesList
              :collectivites-codes="collectivitesCodes"
              :region="currentRegionIso"
              selectable
              :selection="baseTerritorialeSelection"
              @add="add"
              @remove="remove"
            />
          </v-tab-item>
          <v-tab-item>
            <DataGeorisquesTable
              :communes="project.towns"
              selectable
              :selection="geoRisquesSelection"
              @add="add"
              @remove="remove"
            />
          </v-tab-item>
          <v-tab-item>
            <DataINPNTable
              :communes="project.towns"
              selectable
              :selection="inpnSelection"
              @add="add"
              @remove="remove"
            />
          </v-tab-item>
        </v-tabs-items>
      </v-card-text>
    </v-card>
  </v-dialog>
</template>

<script>
import { mdiPlus, mdiPaperclip, mdiClose } from '@mdi/js'

export default {
  props: {
    project: {
      type: Object,
      required: false,
      default: undefined
    },
    section: {
      type: Object,
      required: true
    }
  },
  data () {
    return {
      icons: {
        mdiPlus,
        mdiPaperclip,
        mdiClose
      },
      dialog: false,
      selectedAttachments: [],
      currentTab: null
    }
  },
  computed: {
    collectivitesCodes () {
      return this.project.towns.map(t => t.code)
    },
    currentRegionIso () {
      return this.project.towns[0].region.iso
    },
    baseTerritorialeSelection () {
      return this.selectedAttachments.filter(a => a.source === 'BASE_TERRITORIALE')
    },
    geoRisquesSelection () {
      return this.selectedAttachments.filter(a => a.source === 'GEORISQUES')
    },
    inpnSelection () {
      return this.selectedAttachments.filter(a => a.source === 'INPN')
    }
  },
  async created () {
    const { data } = await this.$supabase.from('pac_sections_data').select('*').match({
      section_id: this.section.id
    })

    this.selectedAttachments = data
  },
  methods: {
    async add (attachment) {
      const { data } = await this.$supabase.from('pac_sections_data').insert([{
        ...attachment,
        section_id: this.section.id
      }]).select()

      this.selectedAttachments = this.selectedAttachments.concat(data)
    },
    async remove (attachmentUrl) {
      this.selectedAttachments = this.selectedAttachments.filter((s) => {
        return s.url !== attachmentUrl
      })

      await this.$supabase.from('pac_sections_data').delete().match({
        url: attachmentUrl,
        section_id: this.section.id
      })
    }
  }
}
</script>
