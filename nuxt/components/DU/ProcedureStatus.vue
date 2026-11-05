<script>
import { mdiCheckCircle } from '@mdi/js'
import { displayProcedureStatus, ProcedureStatus } from '~/store/procedure'

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
  computed: {
    icon() {
      return this.value === ProcedureStatus.Opposable
        ? mdiCheckCircle
        : undefined
    },
    label() {
      return displayProcedureStatus(this.value)
    },
  },
}
</script>

<template>
  <FRBadge :class="`du-procedure-status--${value}`"
           :sm="sm">
    <FRIcon v-if="icon"
            :value="icon" />
    {{ label }}
  </FRBadge>
</template>

<style>
.du-procedure-status--abandoned.fr-badge {
  --fr-badge__bg: #f6f6f6;
  --fr-badge__color: #929292;
}
.du-procedure-status--approved.fr-badge {
  --fr-badge__bg: #c3fad5;
  --fr-badge__color: #297254;
}
.du-procedure-status--canceled.fr-badge {
  --fr-badge__bg: #ffe9e6;
  --fr-badge__color: #b34000;
}
.du-procedure-status--in-planning.fr-badge {
  --fr-badge__bg: #feecc2;
  --fr-badge__color: #6e445a;
}
.du-procedure-status--in-progress.fr-badge {
  --fr-badge__bg: #e9edfe;
  --fr-badge__color: #2f4077;
}
.du-procedure-status--obsolete.fr-badge {
  --fr-badge__bg: #f6f6f6;
  --fr-badge__color: #929292;
}
.du-procedure-status--opposable.fr-badge {
  --fr-badge__bg: #c3fad5;
  --fr-badge__color: #297254;
}
.du-procedure-status--opposable.fr-badge .v-icon {
  --fr-badge__color: #18753c;
}
.du-procedure-status--previous.fr-badge {
  --fr-badge__bg: #ededed;
  --fr-badge__border: #ddd;
  --fr-badge__color: #666;
}
.du-procedure-status--repealed.fr-badge {
  --fr-badge__bg: #ffe9e6;
  --fr-badge__color: #b34000;
}
</style>
