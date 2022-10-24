<template>
  <v-img
    :src="src"
    class="floating-shape"
    :height="`${size || height}px`"
    :width="`${size || width}px`"
    :style="style"
    contain
  />
</template>

<script>
/* WARNING This component parent need to have a position relative */
export default {
  props: {
    top: {
      type: Number,
      default: 0
    },
    left: {
      type: Number,
      default: 0
    },
    right: {
      type: Number,
      default: 0
    },
    bottom: {
      type: Number,
      default: 0
    },
    src: {
      type: String,
      required: true
    },
    size: {
      type: Number,
      default: 0
    },
    height: {
      type: Number,
      default: 40
    },
    width: {
      type: Number,
      default: 40
    }
  },
  computed: {
    style () {
      return {
        top: this.top ? `${this.top}px` : '',
        left: this.left ? `${this.left}px` : '',
        right: this.right ? `${this.right}px` : '',
        bottom: this.bottom ? `${this.bottom}px` : ''
      }
    }
  }
}
</script>

<style scoped>
.floating-shape {
  position: absolute
}
</style>
