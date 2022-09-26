<template>
  <LayoutsCustomApp>
    <template #headerPageTitle>
      - Trame du PAC {{ departement.nom_departement }}
    </template>
    <PACEditingTrame
      v-if="!loading"
      :pac-data="PAC"
      table="pac_sections_region"
      :table-keys="{
        region: region.code
      }"
    />
    <VGlobalLoader v-else />
  </LayoutsCustomApp>
</template>
<script>
import regions from '@/assets/data/Regions.json'
import unifiedPAC from '@/mixins/unifiedPac.js'

export default {
  mixins: [unifiedPAC],
  async asyncData ({ $content }) {
    const PAC = await $content('PAC', {
      deep: true,
      text: true
    }).fetch()

    const originalPAC = PAC.map((section) => {
      return Object.assign({}, section)
    })

    return {
      PAC,
      originalPAC // This is a clone of the row data so we can perform delete on PAC.
    }
  },
  data () {
    return {
      region: null,
      regionSectionsSub: null,
      loading: true
    }
  },
  async mounted () {
    const adminAccess = await this.$auth.getRegionAccess()

    if (!adminAccess) { this.$router.push('/') }

    this.region = regions.find(r => r.code === adminAccess.region)

    this.subscribeToBdd()
    window.addEventListener('focus', () => {
      this.subscribeToBdd()
    })

    const { data: regionSections } = await this.$supabase.from('pac_sections_region').select('*').eq('region', this.region.code)

    // Merge data of multiple PACs using unifiedPac.js mixin.
    this.PAC = this.unifyPacs([regionSections, this.PAC])

    this.loading = false
  },
  beforeDestroy () {
    this.$supabase.removeSubscription(this.regionSectionsSub)
  },
  methods: {
    subscribeToBdd () {
      if (this.regionSectionsSub) {
        this.$supabase.removeSubscription(this.regionSectionsSub)
      }

      this.regionSectionsSub = this.$supabase.from(`pac_sections_regiont:region=eq.${this.region.code}`).on('*', (update) => {
        this.spliceSection(this.PAC, update)
      }).subscribe()
    }
  }
}
</script>
