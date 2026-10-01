<script>
export default {
  props: {
    label: {
      default: '',
      type: String
    },
    value: {
      default: () => [],
      type: Array
    }
  },
  computed: {
    departmentCode () {
      return this.$route.params.code_departement?.padStart(2, '0') || null
    },
    dialogActive: {
      get () {
        return !!this.$route.query.perimetre
      },
      set (newValue) {
        return this.$router.push({
          query: {
            ...this.$route.query,
            perimetre: newValue || undefined
          }
        })
      }
    }
  }
}
</script>

<template>
  <li>
    <DULink @actuated="dialogActive = true">
      Périmètre&nbsp;: {{ value.length }} membre{{ value.length === 1 ? '' : 's' }}
    </DULink>
    <DUDialog v-model="dialogActive">
      <DUHeading :level="3">
        <div>{{ label }}</div>
        <div>
          <strong>Périmètre&nbsp;: {{ value.length }} membre{{ value.length === 1 ? '' : 's' }}</strong>
        </div>
      </DuHeading>
      <DULinksList>
        <DULink
          v-for="member in value"
          :key="member.code"
          :to="{
            params: {
              code_collectivite: member.code,
              code_departement: departmentCode
            },
            query: {
              vue: $route.query.vue
            }
          }"
        >
          {{ member.name }} ({{ member.code }})
        </DULink>
      </DULinksList>
    </DUDialog>
  </li>
</template>
