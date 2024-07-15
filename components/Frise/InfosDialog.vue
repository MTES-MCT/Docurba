
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
      <div class="text-right pr-2 pt-2">
        <v-btn color="primary" text @click="dialog = false">
          Fermer x
        </v-btn>
      </div>
      <v-card-title class="text-h5 d-flex flex-column">
        <div>Informations générales</div>
      </v-card-title>

      <v-card-text class="pt-4">
        <v-container>
          <v-row>
            <v-col cols="12">
              <InputsEditableText v-model="infos.typePlan" class="typo--text" label="Type de plan:" compact />
            </v-col>
            <v-col cols="12">
              <InputsEditableText v-model="infos.typePlan" class="typo--text" label="Type de procédure:" compact />
            </v-col>
            <v-col cols="12">
              <InputsEditableText v-model="infos.typePlan" class="typo--text" label="Numéro de procédure:" compact />
            </v-col>
            <v-col cols="12">
              <InputsEditableText v-model="infos.typePlan" class="typo--text" label="Nom de la procédure:" compact />
            </v-col>
            <v-col cols="12">
              <InputsEditableText v-model="infos.typePlan" class="typo--text" label="Tient lieu de PLH (PLUiH):" compact />
            </v-col>
            <v-col cols="12">
              <InputsEditableText v-model="infos.typePlan" class="typo--text" label="Tient lieu de PDU:" compact />
            </v-col>
            <v-col cols="12">
              <InputsEditableText v-model="infos.typePlan" class="typo--text" label="PDU obligatoire:" compact />
            </v-col>
            <v-col cols="12">
              <InputsEditableText v-model="infos.typePlan" class="typo--text" label="Procédure sectorielle:" compact />
            </v-col>
            <v-col cols="12">
              <InputsEditableText v-model="infos.typePlan" class="typo--text" label="Tient lieu de SCOT:" compact is-switch />
            </v-col>
            <v-col cols="12">
              <InputsEditableText v-model="infos.typePlan" class="typo--text" label="Collectivité en charge:" compact />
            </v-col>
            <v-col cols="12">
              <InputsEditableText v-model="infos.typePlan" class="typo--text" label="Collectivité en charge d’origine:" compact />
            </v-col>
            <v-col cols="12">
              <InputsEditableText v-model="infos.typePlan" class="typo--text" label="Chargé d’étude:" compact />
            </v-col>
            <v-col cols="12">
              <InputsEditableText v-model="infos.typePlan" class="typo--text" label="Type de maîtrise d’oeuvre:" compact />
            </v-col>
            <v-col cols="12">
              <InputsEditableText v-model="infos.typePlan" class="typo--text" label="Publication GPU:" compact />
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
