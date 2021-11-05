<template>
  <v-btn outlined class="mt-auto" color="primary" @click="openDialog">
    {{ text }}
    <client-only>
      <LoginDialog v-model="openLogin" />
      <DocumentsDialog v-if="$user.id" v-model="openDocs" />
    </client-only>
  </v-btn>
</template>

<script>
export default {
  props: {
    text: {
      type: String,
      default: 'Connexion'
    }
  },
  data () {
    return {
      openLogin: false,
      openDocs: false
    }
  },
  methods: {
    openDialog () {
      if (this.$user && this.$user.id) {
        this.openDocs = true
      } else {
        this.openLogin = true
      }
    }
  }
}
</script>
