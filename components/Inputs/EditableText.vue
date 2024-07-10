<template>
  <div class="d-flex align-center">
    <div class="mr-3">
      {{ label }}
    </div>
    <div
      v-if="!editMode"
      ref="editableTextRef"
      :style="{
        height: compact ? '20px' : '78px',
        'min-width': '50px'
      }"
      class="d-flex align-center justify-center text-center"
      :class="textClass"
      @click="editModeOn"
    >
      <div>
        {{ value }}
      </div>

      <v-btn icon class="ml-2">
        <v-icon>{{ icons.mdiPencil }}</v-icon>
      </v-btn>
    </div>

    <v-text-field
      v-else
      ref="editableTextRef"
      v-model="valTxt"
      :dense="compact"
      class="align-center justify-center v-editabletext"
      filled
      placeholder="Type & Press Enter"
      @blur="setValue"
      @keyup.enter="setValue"
    >
      <template #append-outer>
        <div class="d-flex">
          <v-btn
            depressed
            color="primary"
            height="40"
            class="mr-2"
            @click="editMode = false"
          >
            <v-icon>{{ icons.mdiCheck }}</v-icon>
          </v-btn>
          <v-btn
            color="primary"
            outlined
            depressed
            height="40"
            @click="editMode = false"
          >
            <v-icon>{{ icons.mdiClose }}</v-icon>
          </v-btn>
        </div>
      </template>
    </v-text-field>
  </div>
</template>

<script>
import { mdiCheck, mdiClose, mdiPencil } from '@mdi/js'

export default
{
  name: 'EditableText',
  props: {
    value: {
      type: String,
      default: () => ''
    },
    textClass: {
      type: String,
      default: () => ''
    },
    compact: {
      type: Boolean,
      default: () => false
    },
    label: {
      type: String,
      default: () => ''
    }
  },
  data () {
    return {
      editMode: false,
      valTxt: '',
      icons: {
        mdiCheck,
        mdiClose,
        mdiPencil
      }
    }
  },
  methods: {
    editModeOn () {
      this.editMode = true
      // await nextTick()
      // this.editableTextRef.focus()
    },
    setValue () {
      // model = this.valTxt
      this.$emit('input', this.valTxt)
      // this.editableTextRef.blur()
      this.editMode = false
    }
  }
}
// const props = defineProps({ textClass: String, compact: Boolean })
// const model = defineModel()

// const editMode = ref(false)
// const valTxt = ref(model.value)
// const editableTextRef = ref(null)

// async function editModeOn () {
//   editMode.value = true
//   await nextTick()
//   editableTextRef.value.focus()
// }
// async function setValue () {
//   model.value = valTxt.value
//   editableTextRef.value.blur()
//   editMode.value = false
// }
</script>

<style>
.v-editabletext .v-input__append-outer{
  margin-top: 0px !important;
  align-self: baseline !important;
}
</style>
