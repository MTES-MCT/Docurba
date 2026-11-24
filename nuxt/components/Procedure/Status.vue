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
  <DUBadge
    :class="elementClass"
    sm
  >
    <VIcon
      v-if="value === 'Opposable'"
      x-small
    >
      {{ icons.mdiCheckCircle }}
    </VIcon>
    {{ value }}
  </DUBadge>
</template>

<style>
.du-badge.du-procedure-status--abandonne {
  --du-badge__bg: #f6f6f6;
  --du-badge__color: #929292;
}
.du-badge.du-procedure-status--abroge {
  --du-badge__bg: #ffe9e6;
  --du-badge__color: #b34000;
}
.du-badge.du-procedure-status--annule {
  --du-badge__bg: #ffe9e6;
  --du-badge__color: #b34000;
}
.du-badge.du-procedure-status--approuve {
  --du-badge__bg: #c3fad5;
  --du-badge__color: #297254;
}
.du-badge.du-procedure-status--caduc {
  --du-badge__bg: #f6f6f6;
  --du-badge__color: #929292;
}
.du-badge.du-procedure-status--en-cours {
  --du-badge__bg: #e9edfe;
  --du-badge__color: #2f4077;
}
.du-badge.du-procedure-status--en-projet {
  --du-badge__bg: #feecc2;
  --du-badge__color: #6e445a;
}
.du-badge.du-procedure-status--opposable {
  --du-badge__bg: #c3fad5;
  --du-badge__color: #297254;
}
.du-badge.du-procedure-status--opposable > .v-icon {
  color: #18753c;
}
.du-badge.du-procedure-status--precedent {
  --du-badge__bg: #ededed;
  --du-badge__border: #ddd;
  --du-badge__color: #666;
}
</style>
