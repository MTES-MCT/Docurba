<template>
  <div class="sliding-tabs">
    <div
      v-if="isMounted"
      class="sliding-tabs__overlay"
      :style="overlayStyle"
    />

    <div v-for="option in options" :key="option.value" class="sliding-tabs__option">
      <input
        :id="option.value"
        ref="radioRefs"
        class="sliding-tabs__option__input"
        type="radio"
        :value="option.value"
        :checked="option.value === value"
        @change="$emit('input', option.value)"
      >
      <label
        :for="option.value"
        class="sliding-tabs__option__label"
      >
        {{ option.label }}
      </label>
    </div>
  </div>
</template>

<script>
export default {
  model: {
    prop: 'value',
    event: 'input'
  },
  props: {
    options: {
      type: Array,
      required: true
    },
    value: {
      type: String,
      required: true
    }
  },
  data () {
    return {
      isMounted: false
    }
  },
  computed: {
    overlayStyle () {
      const checkedContainer = this.$refs.radioRefs.find(r => r.value === this.value)?.parentElement

      if (!checkedContainer) { return {} }

      return {
        top: `${checkedContainer.offsetTop}px`,
        left: `${checkedContainer.offsetLeft}px`,
        width: `${checkedContainer.offsetWidth}px`,
        height: `${checkedContainer.offsetHeight}px`
      }
    }
  },
  mounted () {
    this.isMounted = true
  }
}
</script>

<style scoped>
.sliding-tabs {
  position: relative;
  height: 5rem;
  display: flex;
  align-items: center;
  gap: 0.5rem;
  border: 1px solid #E3CF50;
  border-radius: 0.5rem;
  background-color: #FCE552;
  padding: 0 0.75rem;
}

.sliding-tabs__overlay {
  position: absolute;
  border-radius: 0.5rem;
  background-color: #FCEEAC;
  transition: all 200ms ease-in-out;
}

.sliding-tabs__option {
  z-index: 1;
}

.sliding-tabs__option__input {
  position: absolute;
  visibility: hidden;
}

.sliding-tabs__option__label {
  height: 3.5rem;
  display: flex;
  align-items: center;
  cursor: pointer;
  padding: 0.5rem 1rem;
  font-weight: 700;
}

@media screen and (max-width: 960px) {
  .sliding-tabs {
    flex-direction: column;
    height: auto;
    padding: 0.75rem 0.75rem;
  }
}
</style>
