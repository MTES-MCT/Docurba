<template>
  <div>
    <div class="mb-2">
      <slot />
    </div>
    <v-radio-group
      v-model="docType"
      class="mb-2"
      hide-details
      row
      :error="!!errorMessages[0]"
      @change="$emit('input', docType)"
    >
      <v-radio
        v-for="(item, i) in items"
        :key="i"
        class="black--text pa-6 d-flex flex-grow-1"
        :class="{'radio-border': docType !== item.value, 'radio-border-active': docType === item.value}"
        :label="item.label"
        :value="item.value"
      />
    </v-radio-group>
    <div class="error--text v-messages pl-3">
      {{ errorMessages[0] }}
    </div>
  </div>
</template>

<script>
export default {
  name: 'VBigRadio',
  props: {
    value: {
      type: String,
      default: () => null
    },
    items: {
      type: Array,
      default: () => []
    },
    errorMessages: {
      type: Array,
      default: () => []
    }
  },
  data () {
    return {
      docType: null
    }
  }
}
</script>

<style lang="scss" >

.radio-border-active{
   border: solid 1px var(--v-primary-base);
    // width: 200px;
    label {
      color: black !important;
    }
}

.radio-border{
    border: solid 1px  var(--v-g300-base);
    // width: 200px;
    label {
      color: black !important;
    }
}
</style>
