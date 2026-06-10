<script setup lang="ts">
import { computed, ref, useTemplateRef, watch } from 'vue'
import type { Options } from '@/data/Option'
import FrButton from '@/components/FrButton.vue'

interface Props {
  lg?: boolean
  options: Options<string | (() => void)>
  sm?: boolean
}

const {
  lg = false,
  options,
  sm = false,
} = defineProps<Props>()

const active = ref(false)

const element = useTemplateRef<HTMLDivElement>('element')
const trigger = useTemplateRef<typeof FrButton>('trigger')

const optionHeight = computed(() => lg ? 3 : sm ? 2 : 2.5)
const optionsCount = computed(() => {
  let optionsCount = 0

  for (const option of options) {
    optionsCount += 1

    if ('options' in option) {
      optionsCount += option.options.length
    }
  }

  return optionsCount
})

watch(active, (newActive) => {
  if (newActive) {
    window.addEventListener('click', clickListener)
  } else {
    window.removeEventListener('click', clickListener)
  }
})

function clickListener(event: PointerEvent) {
  if (
    !element.value
    || event.target === element.value
    || event.composedPath().includes(element.value)
  ) return

  close()
}

function close(focusTrigger: boolean = false) {
  if (!active.value) return

  active.value = false

  if (!focusTrigger || !trigger.value || !trigger.value.$el) return

  trigger.value.$el.focus()
}

function toggle() {
  active.value = !active.value
}
</script>

<template>
  <div class="fr-menu"
       :class="{ 'fr-menu--active': active }"
       ref="element"
       :style="{ '--height': `${optionHeight * optionsCount}rem` }">
    <slot :active="active"
          class-name="fr-icon--after fr-icon--after-arrow-down-s-line fr-menu__button"
          :close="close"
          name="trigger"
          :ref="trigger"
          :toggle="toggle">
      <FrButton :active="active"
                class="fr-icon--after fr-icon--after-arrow-down-s-line fr-menu__button"
                :lg="lg"
                ref="trigger"
                :sm="sm"
                tertiary-borderless
                @actuated="toggle()"
                @keydown.esc="close()">
        <slot />
      </FrButton>
    </slot>
    <ul class="fr-menu__body">
      <template v-for="option in options"
                :key="'value' in option ? option.value : option.label">
        <li v-if="'value' in option">
          <FrButton :disabled="option.disabled"
                    :lg="lg"
                    :sm="sm"
                    start
                    tertiary-borderless
                    :to="
                      typeof option.value === 'string'
                        ? option.value
                        : undefined
                    "
                    @actuated="
                      typeof option.value === 'string'
                        ? undefined
                        : option.value()
                    "
                    @keydown.esc="close(true)">{{ option.label }}</FrButton>
        </li>
        <template v-else>
          <li>
            <FrButton disabled
                      :lg="lg"
                      :sm="sm"
                      start
                      tertiary-borderless>{{ option.label }}</FrButton>
          </li>
          <li v-for="subOption in option.options"
              :key="subOption.label">
            <FrButton :disabled="subOption.disabled"
                      :lg="lg"
                      :sm="sm"
                      start
                      tertiary-borderless
                      :to="
                        typeof subOption.value === 'string'
                          ? subOption.value
                          : undefined
                      "
                      @actuated="
                        typeof subOption.value === 'string'
                          ? undefined
                          : subOption.value()
                      "
                      @keydown.esc="close(true)">{{ subOption.label }}</FrButton>
          </li>
        </template>
      </template>
    </ul>
  </div>
</template>

<style>
.fr-menu {
  display: grid;
  position: relative;
}
.fr-menu--active .fr-menu__body {
  filter: drop-shadow(var(--shadow-overlap));
  height: var(--height);
}
.fr-menu--active .fr-menu__button::after {
  transform: rotate(-180deg);
}
.fr-menu__body {
  align-content: end;
  background-color: var(--color-grey-1000-100);
  display: grid;
  height: 0;
  left: 0;
  list-style: none;
  margin-bottom: 0;
  margin-top: 0;
  min-width: 100%;
  overflow: hidden;
  padding-left: 0;
  position: absolute;
  top: 100%;
  transition-duration: .3s;
  transition-property: filter,
                       height;
  width: max-content;
  z-index: 1;
}
.fr-menu__body li {
  display: grid;
}
.fr-menu__button::after {
  transition: transform .3s;
}
</style>
