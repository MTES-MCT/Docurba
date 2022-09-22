<template>
  <LayoutsCustomApp>
    <template #headerPageTitle>
      - Trame du PAC {{ departement.nom_departement }}
    </template>
    <v-container v-if="!loading" fluid>
      <v-row>
        <v-col :cols="collapsedTree ? 1 : 4" class="collapse-transition">
          <client-only>
            <PACEditingTreeview
              :pac-data="PAC"
              :collapsed="collapsedTree"
              table="pac_sections_dept"
              :table-keys="{
                dept: departementCode
              }"
              :dept="departementCode"
              @open="selectSection"
              @collapse="collapsedTree = !collapsedTree"
            />
          </client-only>
        </v-col>
        <v-col v-if="selectedSection" :cols="collapsedTree ? 11 : 8" class="fill-height collapse-transition">
          <PACEditingContentSection
            :section="selectedSection"
            :pac-data="PAC"
            table="pac_sections_dept"
            :match-keys="{
              dept: departementCode,
            }"
          />
        </v-col>
        <v-col v-else cols="">
          <v-card flat color="g100">
            <v-card-text>Selectionnez une section à éditer.</v-card-text>
          </v-card>
        </v-col>
      </v-row>
    </v-container>
    <VGlobalLoader v-else />
  </LayoutsCustomApp>
</template>

<script>
import unified from 'unified'

import remarkParse from 'remark-parse'
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
      collapsedTree: false,
      selectedSection: null,
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
    const mdParser = unified().use(remarkParse)
    this.mdParser = mdParser

    const { data: adminAccess } = await this.$supabase.from('admin_users_dept').select('dept').match({
      user_id: this.$user.id,
      user_email: this.$user.email,
      role: 'ddt'
    })

    if (!adminAccess || !adminAccess.length) { this.$router.push('/') }

    // eslint-disable-next-line eqeqeq
    this.departement = departements.find(d => d.code_departement == adminAccess[0].dept)

    this.subscribeToBdd()
    window.addEventListener('focus', () => {
      this.subscribeToBdd()
    })

    const { data: deptSections } = await this.$supabase.from('pac_sections_dept').select('*').eq('dept', this.departementCode)

    // Merge data of multiple PACs using unifiedPac.js mixin.
    this.PAC = this.unifyPacs([deptSections, this.PAC])

    this.loading = false
  },
  beforeDestroy () {
    this.$supabase.removeSubscription(this.deptSectionsSub)
  },
  methods: {
    subscribeToBdd () {
      if (this.projectSectionsSub) {
        this.$supabase.removeSubscription(this.projectSectionsSub)
      }

      this.deptSectionsSub = this.$supabase.from(`pac_sections_dept:dept=eq.${this.departementCode}`).on('*', (update) => {
        this.spliceSection(this.PAC, update)
      }).subscribe()
    },
    selectSection (section) {
      const { text, titre, path, slug, dir, ordre } = this.PAC.find(s => s.path === section.path)

      this.selectedSection = {
        text,
        titre,
        path,
        slug,
        dir,
        ordre,
        dept: this.departementCode
      }
    }
    // async addNewSection (newSection) {
    //   newSection.dept = this.departementCode
    //   const { data: savedSection, err } = await this.$supabase.from('pac_sections_dept').insert([newSection])

    //   if (savedSection && !err) {
    //     // console.log(savedSection)
    //     this.PAC.push(Object.assign({
    //       body: this.mdParser.parse(savedSection.text)
    //     }, savedSection[0]))
    //   } else {
    //     // eslint-disable-next-line no-console
    //     console.log('error adding new section', savedSection, err)
    //   }
    // },
    // async deleteSection (deletedSection) {
    //   const { data, err } = await this.$supabase
    //     .from('pac_sections_dept')
    //     .delete()
    //     .match({
    //       dept: this.departementCode,
    //       path: deletedSection.path
    //     })

    //   // if (data && !err) {
    //   //   const deletedSectionIndex = this.PAC.findIndex(s => s.path === deletedSection.path)
    //   //   const originalSection = this.originalPAC.find(s => s.path === deletedSection.path)

    //   //   if (originalSection) {
    //   //     this.PAC.splice(deletedSectionIndex, 1, originalSection)
    //   //   } else { this.PAC.splice(deletedSectionIndex, 1) }
    //   // } else {
    //   //   // eslint-disable-next-line no-console
    //   //   console.log('err deleting a section')
    //   // }
    // }
  }
}
</script>

<style scoped>
.collapse-transition {
  transition: max-width 200ms;
}
</style>
