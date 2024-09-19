<template>
  <div class="d-flex align-center">
    <div v-if="!hideLabel" class="mr-3">
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
    <v-switch
      v-else-if="isSwitch"
      v-model="valTxt"
      inset
    >
      <template #append-outer>
        <div class="d-flex">
          <v-btn
            depressed
            color="primary"
            height="40"
            class="mr-2"
            @click="confirmed"
          >
            <v-icon>{{ icons.mdiCheck }}</v-icon>
          </v-btn>
          <v-btn
            color="primary"
            outlined
            depressed
            height="40"
            @click="cancel"
          >
            <v-icon>{{ icons.mdiClose }}</v-icon>
          </v-btn>
        </div>
      </template>
    </v-switch>
    <!-- @blur="setValue" -->
    <v-text-field
      v-else
      ref="editableTextRef"
      v-model="valTxt"
      :dense="compact"
      class="align-center justify-center v-editabletext"
      filled
      placeholder="Type & Press Enter"
      @keyup.enter="confirmed"
    >
      <template #append-outer>
        <div class="d-flex">
          <v-btn
            depressed
            color="primary"
            height="40"
            class="mr-2"
            @click="confirmed"
          >
            <v-icon>{{ icons.mdiCheck }}</v-icon>
          </v-btn>
          <v-btn
            color="primary"
            outlined
            depressed
            height="40"
            @click="cancel"
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
    },
    isSwitch: {
      type: Boolean,
      default: () => false
    },
    edit: {
      type: Boolean,
      default: () => false
    },
    hideLabel: {
      type: Boolean,
      default: () => false
    }
  },
  data () {
    return {
      tempText: this.value,
      editMode: this.edit,
      valTxt: this.value,
      icons: {
        mdiCheck,
        mdiClose,
        mdiPencil
      }
    }
  },
  // watch: {
  //   value: {
  //     handler (newVal) {
  //       console.log('WATCH ', newVal)
  //       this.valTxt = newVal
  //     },
  //     immediate: true
  //   }
  // },
  methods: {
    confirmed () {
      this.editMode = false
      this.setValue()
      this.$emit('confirmed')
    },
    cancel () {
      this.editMode = false
      this.valTxt = this.tempText
      this.$emit('input', this.tempText)
      this.tempText = ''
      this.$emit('cancel')
    },
    editModeOn () {
      this.tempText = this.value
      this.editMode = true
    },
    setValue () {
      this.$emit('input', this.valTxt)
      this.editMode = false
    }
  }
}
</script>

<style>
.v-editabletext .v-input__append-outer{
  margin-top: 0px !important;
  align-self: baseline !important;
}
</style>
