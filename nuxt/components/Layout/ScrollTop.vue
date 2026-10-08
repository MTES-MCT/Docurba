<script>
import { mdiArrowUp } from '@mdi/js'

export default {
  data () {
    return {
      icons: {
        mdiArrowUp
      }
    }
  },
  methods: {
    scrollTop () {
      window.scrollTo({
        behavior: 'smooth',
        top: 0
      })
    }
  }
}
</script>

<template>
  <DULink
    class="du-layout-scroll-top"
    @actuated="scrollTop()"
  >
    <VIcon small>
      {{ icons.mdiArrowUp }}
    </VIcon>
    Haut de page
  </DULink>
</template>

<style>
.du-layout-scroll-top {
  margin-top: 1rem;
}
</style>
