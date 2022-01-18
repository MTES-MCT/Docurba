<template>
  <LayoutsCustomApp>
    <template #headerPageTitle>
      - Trame du PAC {{ departement.nom_departement }}
    </template>
    <v-container v-if="!loading" fluid>
      <v-row>
        <v-col :cols="collapsedTree ? 1 : 4" class="collapse-transition">
          <client-only>
            <PACTreeviewEditing
              :pac-data="PAC"
              :collapsed="collapsedTree"
              @open="selectSection"
              @add="addNewSection"
              @remove="deleteSection"
              @collapse="collapsedTree = !collapsedTree"
            />
          </client-only>
        </v-col>
        <v-col v-if="selectedSection" cols="" class="fill-height">
          <PACContentSectionEditing :text="selectedSection.text" :titre="selectedSection.titre" @save="saveSection" />
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

export default {
  layout: 'app',
  async asyncData ({ $content }) {
    const PAC = await $content('PAC', {
      deep: true,
      text: true
    }).fetch()

    return {
      PAC
    }
  },
  data () {
    return {
      loading: true,
      collapsedTree: false,
      selectedSection: null,
      departement: { code_departement: 0, nom_departement: '' }
    }
  },
  computed: {
    departementCode () {
      return this.departement.code_departement.toString()
    }
  },
  async mounted () {
    // TODO: This part is the same in the page projects/index.vue and coul be made into a mixin.
    const { data: adminAccess } = await this.$supabase.from('admin_users_dept').select('dept').match({
      user_id: this.$user.id,
      user_email: this.$user.email,
      role: 'ddt'
    })

    if (!adminAccess || !adminAccess.length) { this.$router.push('/') }

    // eslint-disable-next-line eqeqeq
    this.departement = departements.find(d => d.code_departement == adminAccess[0].dept)

    const { data: deptSections } = await this.$supabase.from('pac_sections_dept').select('*').eq('dept', this.departementCode)

    const mdParser = unified().use(remarkParse)
    this.mdParser = mdParser

    deptSections.forEach((section) => {
      section.body = mdParser.parse(section.text)
      const sectionIndex = this.PAC.findIndex(s => s.path === section.path)

      if (sectionIndex >= 0) {
        // The Object Assign here is to keep the order since it's not saved. As could be other properties.
        // Although it might create inconsistenties for versions that get Archived later on.
        this.PAC[sectionIndex] = Object.assign({}, this.PAC[sectionIndex], section)
      } else {
        this.PAC.push(Object.assign({}, section))
      }
    })

    this.loading = false
  },
  methods: {
    selectSection (section) {
      const { text, titre, path, slug, dir } = this.PAC.find(s => s.path === section.path)

      this.selectedSection = {
        text, titre, path, slug, dir
      }
    },
    async saveSection (editedSection) {
      const { data: savedSection } = await this.$supabase.from('pac_sections_dept').select('id').match({
        dept: this.departementCode, // This need to be dynamic.
        path: this.selectedSection.path
      })

      const newData = Object.assign({
        dept: this.departementCode
      }, this.selectedSection, editedSection)

      if (savedSection[0]) { newData.id = savedSection[0].id }

      try {
        if (savedSection[0]) {
          await this.$supabase.from('pac_sections_dept').upsert(newData)
        } else {
          await this.$supabase.from('pac_sections_dept').insert([newData])
        }

        const sectionIndex = this.PAC.findIndex(s => s.path === newData.path)

        // this.PAC[sectionIndex] = newData
        this.PAC.splice(sectionIndex, 1, newData)
      } catch (err) {
        // eslint-disable-next-line no-console
        console.log('Error saving data')
      }
    },
    async addNewSection (newSection) {
      newSection.dept = this.departementCode
      const { data: savedSection, err } = await this.$supabase.from('pac_sections_dept').insert([newSection])

      if (savedSection && !err) {
        // console.log(savedSection)
        this.PAC.push(Object.assign({
          body: this.mdParser.parse(savedSection.text)
        }, savedSection[0]))
      } else {
        // eslint-disable-next-line no-console
        console.log('error adding new section', savedSection, err)
      }
    },
    async deleteSection (deletedSection) {
      const { data, err } = await this.$supabase
        .from('pac_sections_dept')
        .delete()
        .match({
          dept: this.departementCode,
          path: deletedSection.path
        })

      if (data && !err) {
        const deletedSectionIndex = this.PAC.findIndex(s => s.path === deletedSection.path)

        // this.PAC[deletedSectionIndex] = newData
        this.PAC.splice(deletedSectionIndex, 1)
      } else {
        // eslint-disable-next-line no-console
        console.log('err deleting a section')
      }
    }
  }
}
</script>

<style scoped>
.collapse-transition {
  transition: max-width 200ms;
}
</style>
