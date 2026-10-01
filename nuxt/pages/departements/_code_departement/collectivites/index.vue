<script>
export default {
  computed: {
    departmentCode () {
      return this.$route.params.code_departement?.padStart(2, '0') || null
    }
  }
}
</script>

<template>
  <LayoutMain
    :breadcrumb="breadcrumb"
    label="Page collectivités non implémentée"
  >
    <DUButton
      primary
      :to="`/ddt/${departmentCode}/collectivites`"
    >
      Page alternative
    </DUButton>
  </LayoutMain>
</template>
