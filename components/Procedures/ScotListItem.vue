<template>
  <v-list-item :value="scot.code">
    <template #default="{active}">
      <v-list-item-content>
        <v-list-item-title class="font-weight-bold">
          {{ scot.intitule }} ({{ scot.code }})
        </v-list-item-title>
      </v-list-item-content>
      <v-list-item-content>
        <v-list-item-subtitle
          v-for="procedure in scot.procedures"
          :key="procedure.id"
          class="py-2"
        >
          <v-chip small label color="alt-beige" class="font-weight-bold">
            {{ procedure.doc_type }}
          </v-chip>
          <v-chip small label :color="procedure.status === 'opposable' ? 'success-light' : 'bf200'">
            <span
              :class="procedure.status === 'opposable' ? 'success--text' : 'primary--text'"
              class="text-uppercase font-weight-bold"
            >
              {{ procedure.status }}
            </span>
          </v-chip>
        </v-list-item-subtitle>
      </v-list-item-content>
      <template v-if="!validated">
        <v-list-item-action>
          <v-btn
            color="bf200"
            tile
            depressed
            nuxt
            small
            class="font-weight-bold"
            :to="`/frise/${scot.code}`"
          >
            <span class="primary--text">Corriger</span>
            <v-icon small color="primary" class="ml-1">
              {{ icons.mdiArrowRight }}
            </v-icon>
          </v-btn>
        </v-list-item-action>
        <v-list-item-action>
          <v-checkbox :value="active" class="d-flex align-center">
            <template #prepend>
              <span class="primary--text">Valider</span>
            </template>
          </v-checkbox>
        </v-list-item-action>
      </template>
      <v-list-item-action v-else>
        Validés le {{ validationDate }}
      </v-list-item-action>
    </template>
  </v-list-item>
</template>

<script>
import { mdiArrowRight } from '@mdi/js'
import dayjs from 'dayjs'

export default {
  props: {
    scot: {
      type: Object,
      required: true
    },
    validated: {
      type: Boolean,
      default: false
    }
  },
  data () {
    return {
      icons: { mdiArrowRight }
    }
  },
  computed: {
    validationDate () {
      const validation = this.scot.validations[0]
      return dayjs(validation.created_at).format('DD-MM-YYYY')
    }
  }
}
</script>
