<template>
  <v-hover v-slot="{hover}">
    <v-list-item
      :to="shareable ? `/ddt/${project.id}` : `/projets/${project.id}/content`"
      nuxt
      two-line
      @click="$emit('input', false)"
    >
      <v-list-item-content>
        <v-list-item-title>{{ project.name }}</v-list-item-title>
        <v-list-item-subtitle>{{ project.docType }} - {{ placeName }}</v-list-item-subtitle>
      </v-list-item-content>
      <v-list-item-action>
        <div class="d-flex">
          <v-dialog width="500px">
            <template #activator="{on}">
              <v-btn
                v-show="hover && shareable"
                icon
                v-on="on"
                @click.prevent.stop
              >
                <v-icon>{{ icons.mdiPencil }}</v-icon>
              </v-btn>
            </template>
            <template #default="dialog">
              <ProjectsProjectCardForm :project="project" @cancel="dialog.value = false">
                <template #title>
                  Modifier le projet
                </template>
              </ProjectsProjectCardForm>
            </template>
          </v-dialog>
          <v-btn v-show="hover && shareable" icon :to="`/projets/${project.id}/content`" nuxt>
            <v-icon>{{ icons.mdiEye }}</v-icon>
          </v-btn>
          <client-only>
            <v-btn v-show="hover" icon @click.prevent.stop="$print(`/print/${project.id}`)">
              <v-icon>{{ icons.mdiDownload }}</v-icon>
            </v-btn>
          </client-only>
          <v-dialog>
            <template #activator="{on}">
              <v-btn
                v-show="hover && shareable"
                icon
                v-on="on"
                @click.prevent.stop
              >
                <v-icon>{{ icons.mdiShare }}</v-icon>
              </v-btn>
            </template>
            <v-card>
              <v-card-title>Partager le projet</v-card-title>
              <v-card-text>
                <ProjectsSharingForm :project="project" />
              </v-card-text>
            </v-card>
          </v-dialog>
        </div>
      </v-list-item-action>
    </v-list-item>
  </v-hover>
</template>

<script>
import {
  mdiShare, mdiPencil,
  mdiEye, mdiDownload
} from '@mdi/js'

export default {
  props: {
    project: {
      type: Object,
      required: true
    },
    shareable: {
      type: Boolean,
      default: false
    }
  },
  data () {
    return {
      icons: {
        mdiShare,
        mdiPencil,
        mdiEye,
        mdiDownload
      }
    }
  },
  computed: {
    placeName () {
      return this.project.epci ? this.project.epci.label : this.project.towns[0].nom_commune
    }
  }
}
</script>
