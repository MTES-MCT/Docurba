
<template>
  <v-dialog v-model="dialog" width="800">
    <template #activator="{ on, attrs }">
      <v-list-item link v-bind="attrs" v-on="on">
        <v-list-item-title>
          Informations générales
        </v-list-item-title>
      </v-list-item>
    </template>

    <v-card>
      <v-card-title class="text-h5 d-flex flex-column">
        <div>Informations générales</div>
      </v-card-title>

      <v-card-text class="pt-4">
        <v-container>
          <v-row>
            <v-col cols="12">
              <InputsEditableText v-model="infos.typePlan" label="Type de plan:" compact />
            </v-col>
            <v-col cols="12">
              <InputsEditableText v-model="infos.typePlan" label="Type de procédure:" compact />
            </v-col>
          </v-row>
          <v-row>
            <v-col cols="12">
              Périmètre:
            </v-col>
          </v-row>
          <v-row>
            <v-col cols="12">
              <v-btn color="primary" outlined>
                Signaler une erreur
              </v-btn>
            </v-col>
          </v-row>
        </v-container>
      </v-card-text>
    </v-card>
  </v-dialog>
</template>
<script>
import { mdiDotsVertical } from '@mdi/js'

export default
{
  name: 'InfosDialog',
  props: {},
  data () {
    return {
      infos: {
        typePlan: 'toto'
      },
      dialog: false,
      voletQualitatifRaw: null,
      icons: {
        mdiDotsVertical
      }
    }
  },
  computed: {
  },
  async mounted () {

  },
  methods: {

  }
}
</script>
