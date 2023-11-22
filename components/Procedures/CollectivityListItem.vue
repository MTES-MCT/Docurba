<template>
  <v-list-item :value="collectivity.code">
    <template #default="{active}">
      <v-list-item-content>
        <v-list-item-title>{{ collectivity.intitule }} ({{ collectivity.code }})</v-list-item-title>
      </v-list-item-content>
      <v-list-item-content v-if="collectivity.loaded">
        <v-list-item-subtitle v-for="procedure in collectivity.procedures" :key="procedure.id">
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
        <v-list-item-subtitle v-if="!collectivity.procedures.length">
          <v-chip small label color="alt-beige" class="font-weight-bold">
            RNU
          </v-chip>
        </v-list-item-subtitle>
      </v-list-item-content>
      <v-list-item-content v-else>
        <v-progress-circular
          indeterminate
          size="16"
          width="2"
          color="primary"
        />
      </v-list-item-content>
      <template v-if="!validated">
        <v-list-item-action>
          <v-btn
            color="bf200"
            tile
            depressed
            nuxt
            :to="`/ddt/${collectivity.departementCode}/collectivites/${collectivity.code}/commune`"
          >
            <span class="primary--text">Corriger</span>
            <v-icon color="primary">
              {{ icons.mdiArrowRight }}
            </v-icon>
          </v-btn>
        </v-list-item-action>
        <v-list-item-action>
          <v-checkbox :value="active">
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
    collectivity: {
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
      const validation = this.collectivity.validations[0]
      return dayjs(validation.created_at).format('DD-MM-YYYY')
    }
  }
}
</script>
