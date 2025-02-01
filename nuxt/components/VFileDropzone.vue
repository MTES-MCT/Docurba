<template>
  <div>
    <input :ref="'fileInput'" class="d-none" type="file" multiple @change="handleFiles">
    <div @click="clickZone" @drop.prevent="inputFile" @dragenter.prevent @dragover.prevent>
      <slot :openFiles="openFiles" />
    </div>
  </div>
</template>
<script>
export default {
  props: {
    dropOnly: {
      type: Boolean,
      default: false
    }
  },
  methods: {
    clickZone () {
      if (!this.dropOnly) {
        this.$refs.fileInput.click()
      }
    },
    openFiles () {
      this.$refs.fileInput.click()
    },
    handleFiles () {
      const files = this.$refs.fileInput.files
      this.$emit('change', files)
    },
    inputFile (dropEvent) {
      this.$emit('change', dropEvent.dataTransfer.files)
    }
  }
}
</script>
