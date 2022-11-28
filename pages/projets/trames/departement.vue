<template>
  <LayoutsCustomApp>
    <template #headerPageTitle>
      - Trame du PAC {{ departement.nom_departement }}
    </template>
    <PACEditingTrame
      v-if="!loading"
      :pac-data="PAC"
      table="pac_sections_dept"
      :table-keys="{
        dept: departementCode
      }"
    />
    <VGlobalLoader v-else />
  </LayoutsCustomApp>
</template>

<script>
import departements from '@/assets/data/departements-france.json'
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
    return {
      loading: true,
      departement: { code_departement: 0, nom_departement: '' },
      deptSectionsSub: null
    }
  },
  computed: {
    departementCode () {
      return this.departement.code_departement.toString()
    }
  },
  async mounted () {
    const adminAccess = await this.$auth.getDeptAccess()

    if (!adminAccess) { this.$router.push('/') }

    // eslint-disable-next-line eqeqeq
    this.departement = departements.find(d => d.code_departement == adminAccess.dept)

    this.subscribeToBdd()
    window.addEventListener('focus', () => {
      this.subscribeToBdd()
    })

    // const { data: deptSections } = await this.$supabase.from('pac_sections_dept').select('*').eq('dept', this.departementCode)

    const [regionSections, deptSections] = await Promise.all([
      this.fetchSections('pac_sections_region', {
        region: this.departement.code_region
      }),
      this.fetchSections('pac_sections_dept', {
        dept: this.departementCode
      })
    ])

    // Merge data of multiple PACs using unifiedPac.js mixin.
    this.PAC = this.unifyPacs([deptSections, regionSections, this.PAC])

    this.loading = false
  },
  beforeDestroy () {
    this.$supabase.removeChannel(this.deptSectionsSub)
  },
  methods: {
    subscribeToBdd () {
      if (this.projectSectionsSub) {
        this.$supabase.removeChannel(this.projectSectionsSub)
      }

      this.deptSectionsSub = this.$supabase.channel(`public:pac_sections_dept:dept=eq.${this.departementCode}`)
        .on('postgres_changes', { event: '*', schema: 'public', table: 'pac_sections_dept', filter: `dept=eq.${this.departementCode}` }, (update) => {
          this.spliceSection(this.PAC, update)
        }).subscribe()
    }
  }
}
</script>

<style scoped>
.collapse-transition {
  transition: max-width 200ms;
}
</style>
