<script>
export default {
  name: 'Collectivite',
  beforeRouteEnter (to, _from, next) {
    return next({
      name: 'collectivites-code_collectivite',
      params: {
        code_collectivite: to.params.collectiviteId
      }
    })
  }
}
</script>
