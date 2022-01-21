<template>
  <v-hover v-slot="{hover}">
    <v-list-item
      :to="`/projets/${project.id}/content`"
      nuxt
      two-line
      @click="$emit('input', false)"
    >
      <v-list-item-content>
        <v-list-item-title>{{ project.name }}</v-list-item-title>
        <v-list-item-subtitle>{{ project.docType }}</v-list-item-subtitle>
      </v-list-item-content>
      <v-list-item-action>
        <div class="d-flex">
          <v-dialog>
            <template #activator="{on}" width="500px">
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
import { mdiShare, mdiPencil } from '@mdi/js'

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
        mdiPencil
      }
    }
  }
}
</script>
