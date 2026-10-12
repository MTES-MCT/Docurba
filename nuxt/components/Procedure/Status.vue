<script>
import { mdiCheckCircle } from '@mdi/js'

export default {
  props: {
    value: {
      default: '',
      type: String
    }
  },
  data () {
    return {
      icons: {
        mdiCheckCircle
      }
    }
  },
  computed: {
    elementClass () {
      return this.value
        ? `du-procedure-status--${
          this.value.toLowerCase()
            .normalize('NFKD')
            .replace(/[^a-z ]+/g, '')
            .replace(/\s+/g, '-')
        }`
        : undefined
    }
  }
}
</script>

<template>
  <div
    class="du-procedure-status"
    :class="elementClass"
  >
    <VIcon
      v-if="value === 'Opposable'"
      x-small
    >
      {{ icons.mdiCheckCircle }}
    </VIcon>
    {{ value }}
  </div>
</template>

<style>
.du-procedure-status {
  align-items: center;
  border-radius: .25rem;
  column-gap: .25rem;
  display: grid;
  font-size: .75rem;
  font-weight: 700;
  grid-auto-flow: column;
  line-height: 1.25rem;
  padding-left: .375rem;
  padding-right: .375rem;
  text-transform: uppercase;
  white-space: nowrap;
}
.du-procedure-status .v-icon {
  margin-left: -.1875rem;
}
.du-procedure-status--abandonne {
  background-color: #f6f6f6;
  color: #929292;
}
.du-procedure-status--abroge {
  background-color: #ffe9e6;
  color: #b34000;
}
.du-procedure-status--annule {
  background-color: #ffe9e6;
  color: #b34000;
}
.du-procedure-status--approuve {
  background-color: #c3fad5;
  color: #297254;
}
.du-procedure-status--caduc {
  background-color: #f6f6f6;
  color: #929292;
}
.du-procedure-status--en-cours {
  background-color: #e9edfe;
  color: #2f4077;
}
.du-procedure-status--en-projet {
  background-color: #feecc2;
  color: #6e445a;
}
.du-procedure-status--opposable {
  background-color: #c3fad5;
  color: #297254;
}
.du-procedure-status--opposable .v-icon {
  color: #18753c;
}
.du-procedure-status--precedent {
  background-color: #ededed;
  box-shadow: inset 0 0 0 .0625rem #ddd;
  color: #666;
}
</style>
