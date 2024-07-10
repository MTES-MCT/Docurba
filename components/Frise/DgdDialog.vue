
<template>
  <v-dialog v-model="dialog" width="800">
    <template #activator="{ on, attrs }">
      <v-list-item link v-bind="attrs" v-on="on">
        <v-list-item-title>
          DGD
        </v-list-item-title>
      </v-list-item>
    </template>

    <v-card>
      <v-card-title class="text-h5 d-flex flex-column">
        <div>DGD</div>
      </v-card-title>

      <v-card-text class="pt-4">
        <v-container />
      </v-card-text>
    </v-card>
  </v-dialog>
</template>
<script>
import { mdiDotsVertical } from '@mdi/js'

export default
{
  name: 'DgdDialog',
  props: {},
  data () {
    return {
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
