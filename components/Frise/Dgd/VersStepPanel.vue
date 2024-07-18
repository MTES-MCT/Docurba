<template>
  <div>
    <v-divider />
    <v-data-table

      :headers="headers"
      :items="desserts"
      hide-default-footer
      :items-per-page="-1"
      class="elevation-0"
    >
      <template #item="{item}">
        <tr v-if="item.edit">
          <td><v-text-field dense filled label="Étape prévue pour le versement" /></td>
          <td>lul</td>
        </tr>
        <tr v-else>
          <td>selected</td>
          <td>selected</td>
        </tr>
      </template>
    </v-data-table>

    <v-btn outlined color="primary" @click="addNewVersement">
      + Ajouter une étape de versement
    </v-btn>
    <InputsEditableText label="Commentaire:" compact />
  </div>
</template>
<script>
import { mdiMinusCircle, mdiCheckCircle } from '@mdi/js'

export default
{
  name: 'VersStepPanel',
  icons: {
    mdiMinusCircle,
    mdiCheckCircle
  }
}
