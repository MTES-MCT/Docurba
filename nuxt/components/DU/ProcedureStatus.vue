<script>
import { mdiCheckCircle } from '@mdi/js'

export default {
  props: {
    sm: {
      default: false,
      type: Boolean,
    },
    value: {
      default: '',
      type: String,
    },
  },
  data() {
    return {
      icons: {
        mdiCheckCircle,
      },
    }
  },
  computed: {
    elementClass() {
      return this.value
        ? `du-procedure-status--${
          this.value.toLowerCase()
            .normalize('NFKD')
            .replace(/[^a-z ]+/g, '')
            .replace(/\s+/g, '-')
        }`
        : undefined
    },
  },
}
</script>

<template>
  <FRBadge :class="elementClass"
           :sm="sm">
    <FRIcon v-if="value === 'Opposable'"
            :value="icons.mdiCheckCircle" />
    {{ value }}
  </FRBadge>
</template>

<style>
.du-procedure-status--abandonne {
  --fr-badge__bg: #f6f6f6;
  --fr-badge__color: #929292;
}
.du-procedure-status--abroge {
  --fr-badge__bg: #ffe9e6;
  --fr-badge__color: #b34000;
}
.du-procedure-status--annule {
  --fr-badge__bg: #ffe9e6;
  --fr-badge__color: #b34000;
}
.du-procedure-status--approuve {
  --fr-badge__bg: #c3fad5;
  --fr-badge__color: #297254;
}
.du-procedure-status--caduc {
  --fr-badge__bg: #f6f6f6;
  --fr-badge__color: #929292;
}
.du-procedure-status--en-cours {
  --fr-badge__bg: #e9edfe;
  --fr-badge__color: #2f4077;
}
.du-procedure-status--en-projet {
  --fr-badge__bg: #feecc2;
  --fr-badge__color: #6e445a;
}
.du-procedure-status--opposable {
  --fr-badge__bg: #c3fad5;
  --fr-badge__color: #297254;
}
.du-procedure-status--opposable .v-icon {
  --fr-badge__color: #18753c;
}
.du-procedure-status--precedent {
  --fr-badge__bg: #ededed;
  --fr-badge__border: #ddd;
  --fr-badge__color: #666;
}
</style>
