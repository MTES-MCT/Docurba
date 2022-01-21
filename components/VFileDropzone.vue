<template>
  <div>
    <input :ref="'fileInput'" class="d-none" type="file" multiple @change="handleFiles">
    <div @click="$refs['fileInput'].click()" @drop.prevent="inputFile" @dragenter.prevent @dragover.prevent>
      <slot />
    </div>
  </div>
</template>
<script>
export default {
  methods: {
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
