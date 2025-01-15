<template>
  <v-container>
    <v-row>
      <v-col cols="12" class="text-subtitle-1 font-weight-bold">
        {{ $utils.formatProcedureName(procedure, collectivite) }}
        {{ isCommunal ? `(${collectivite?.code})` : '' }}
        <br>
        <span class="text-caption">{{ procedure.id }} - (sudocu: {{ procedure.from_sudocuh }}) parent: {{ procedure.procedure_id }}</span>
      </v-col>
    </v-row>
    <v-row class="mt-0">
      <v-col>
        <div class="text-caption g600--text">
          Statut
        </div>
        <div>
          <v-chip :color="statusColors[procedure.status]" small label class="text-uppercase mr-2">
            {{ procedure.status }}
          </v-chip>
        </div>
      </v-col>
      <v-col>
        <div class="text-caption g600--text">
          Type de procédure
        </div>
        <div>
          {{ procedure.type }}
        </div>
      </v-col>
      <v-col>
        <div class="text-caption g600--text">
          Etape de la procédure
        </div>
        <div>
          {{ step }}
        </div>
      </v-col>
    </v-row>
    <v-row v-if="!censored">
      <v-col cols="12" class="pb-0">
        <v-divider />
      </v-col>
      <v-col cols="12" class="pb-0">
        <p class="font-weight-bold">
          Commentaire / Note
        </p>
        <p v-if="procedure.commentaire">
          {{ procedure.commentaire }}
        </p>
      </v-col>
      <v-col cols="12" class="pb-0">
        <v-divider />
      </v-col>
      <v-col cols="12" class="pb-0 d-flex">
        <DashboardDUModalPerimetre :perimetres="procedure.procedures_perimetres" />
        <nuxt-link :to="`/frise/${procedure.id}`">
          <span class="primary--text text-decoration-underline mr-4">
            Feuille de route
          </span>
        </nuxt-link>
        <nuxt-link
          class="primary--text text-decoration-underline mr-4"
          :to="`/ddt/${$route.params.departement}/pac?search=${$route.params.collectiviteId}`"
        >
          PAC
        </nuxt-link>

        <v-dialog v-model="dialog" width="500">
          <template #activator="{ on, attrs }">
            <span class="error--text text-decoration-underline ml-auto align-center" v-bind="attrs" v-on="on">
              Supprimer
            </span>
          </template>

          <v-card>
            <v-card-title class="text-h5 error white--text">
              Cette action est irréversible.
            </v-card-title>

            <v-card-text class="pt-4">
              Êtes-vous sur de vouloir supprimer cette procédure ? Il ne sera pas possible de revenir en arrière.
            </v-card-text>

            <v-divider />

            <v-card-actions>
              <v-spacer />
              <v-btn color="primary" text @click="dialog = false">
                Annuler
              </v-btn>
              <v-btn v-if="!censored" color="error" depressed @click="archiveProcedure(procedure.id)">
                Supprimer
              </v-btn>
            </v-card-actions>
          </v-card>
        </v-dialog>
      </v-col>
    </v-row>
    <v-row v-else>
      <v-col cols="12" class="pb-0">
        <v-divider />
      </v-col>
      <v-col cols="12" class="d-flex align-center justify-end pb-0">
        <DashboardDUModalPerimetre :perimetres="procedure.procedures_perimetres" />
        <v-spacer />
        <v-btn text color="primary" :to="{name: 'frise-procedureId', params: {procedureId: procedure.id}}">
          <v-icon small color="primary" class="mr-2">
            {{ icons.mdiArrowRight }}
          </v-icon>
          Feuille de route
        </v-btn>
      </v-col>
    </v-row>
  </v-container>
</template>
<script>
import { mdiArrowRight } from '@mdi/js'
import BaseDUProcedureItem from '@/mixins/BaseDUProcedureItem.js'

export default {
  mixins: [BaseDUProcedureItem],
  props: {
    procedure: {
      type: Object,
      required: true
    },
    collectivite: {
      type: Object,
      required: true
    },
    censored: {
      type: Boolean,
      default: () => false
    }
  },
  data () {
    return {
      icons: {
        mdiArrowRight
      },
      dialog: false
    }
  },
  computed: {
    isCommunal () {
      return this.procedure.procedures_perimetres.length === 1
    }
  },
  methods: {
    async  archiveProcedure (idProcedure) {
      try {
        const { error } = await this.$supabase
          .from('procedures')
          .delete()
          .eq('id', idProcedure)

        if (error) { throw error }
        this.$emit('delete', idProcedure)
        this.dialog = false
      } catch (error) {
        // eslint-disable-next-line no-console
        console.log(error)
      }
    }
  }
}
</script>
