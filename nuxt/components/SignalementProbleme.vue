<template>
  <v-btn v-if="$user?.id" color="primary" outlined @click="openSignalementForm">
    Signaler un problème
  </v-btn>
</template>

<script>
export default {
  methods: {
  // https://tally.so/help/developer-resources#2f676e40530a460ea6a634b8441f6001
  // https://tally.so/help/hidden-fields
  // https://tally.so/help/pre-populate-form-fields#d145bec3bde2446b8ae17a4357494950
  // originPage hidden field pour capturer l'URL
    openSignalementForm () {
      const hiddenFields = {
        email: this.$user.email,
        side: this.$user.profile.side,
        departement: this.$user.profile.departement,
        collectivite_id: this.$user.profile.collectivite_id
      }

      window.Tally.openPopup('3qjW27', {
        hideTitle: true,
        width: 500,
        hiddenFields
      })
    }
  }

}
</script>
