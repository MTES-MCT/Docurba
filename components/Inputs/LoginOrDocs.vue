<template>
  <v-btn outlined class="mt-auto" color="primary" @click="openDialog">
    {{ text }}
    <client-only>
      <LoginDialog v-model="openLogin" />
      <DocumentsDialog v-if="$user.id" v-model="openDocs" @created="navToProject" />
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
    },
    // This is a duplicate from default layout
    navToProject (project) {
      this.openDocs = false
      this.$router.push(`/projets/${project.id}`)
    }
  }
}
</script>
