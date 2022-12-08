<template>
  <LayoutsCustomApp>
    <template #headerPageTitle>
      - {{ region.name }}
    </template>
    <PACEditingTrame
      v-if="!loading"
      :pac-data="PAC"
      table="pac_sections_region"
      :table-keys="{
        region: region.code
      }"
      :readonly-dirs="[]"
    />
    <VGlobalLoader v-else />
  </LayoutsCustomApp>
</template>
<script>
import regions from '@/assets/data/Regions.json'
import unifiedPAC from '@/mixins/unifiedPac.js'

export default {
  mixins: [unifiedPAC],
  layout: 'app',
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
    const region = regions.find(r => r.code === this.$route.params.regionCode)

    return {
      region,
      regionSectionsSub: null,
      loading: true
    }
  },
  async mounted () {
    const adminAccess = await this.$auth.getRegionAccess(true)
    const currentRegionAccess = adminAccess.find(access => access.region === this.region.code)

    if (!adminAccess.length || !currentRegionAccess) { this.$router.push('/') }

    // this.region = regions.find(r => r.code === adminAccess.region)

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
    this.$supabase.removeChannel(this.regionSectionsSub)
  },
  methods: {
    subscribeToBdd () {
      if (this.regionSectionsSub) {
        this.$supabase.removeChannel(this.regionSectionsSub)
      }

      this.regionSectionsSub = this.$supabase.channel(`public:pac_sections_region:region=eq.${this.region.code}`)
        .on('postgres_changes', { event: '*', schema: 'public', table: 'pac_sections_region', filter: `region=eq.${this.region.code}` }, (update) => {
          this.spliceSection(this.PAC, update)
        }).subscribe()
    }
  }
}
</script>
