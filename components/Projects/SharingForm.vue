<template>
  <v-row>
    <v-col cols="12">
      <v-text-field v-model="newShareEmail" label="email" />
    </v-col>
  </v-row>
</template>

<script>
export default {
  props: {
    project: {
      type: Object,
      required: true
    }
  },
  data () {
    return {
      newShareEmail: ''
    }
  }
}
</script>
