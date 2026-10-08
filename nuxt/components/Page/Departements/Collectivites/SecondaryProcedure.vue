<script>
import { mdiArrowRight } from '@mdi/js'

export default {
  props: {
    value: {
      default: () => ({}),
      type: Object
    }
  },
  data () {
    return {
      icons: {
        mdiArrowRight
      }
    }
  },
  computed: {
    departmentCode () {
      return this.$route.params.code_departement?.padStart(2, '0') || null
    },
    territorialAuthorityCode () {
      return this.$route.params.code_collectivite || null
    }
  }
}
</script>

<template>
  <DUCard
    :to="{
      name: 'departements-code_departement-collectivites-code_collectivite-procedures-id_procedure',
      params: {
        code_collectivite: territorialAuthorityCode,
        code_departement: departmentCode,
        id_procedure: value.id
      }
    }"
  >
    <DUGroup
      start
      xxs
    >
      <DUHeading
        ellipsis
        :level="4"
        strong
        :title="value.name"
      >
        {{ value.name }}
      </DUHeading>
      <DUList sm>
        <li v-if="value.prescriptionDate">
          Prescrit le {{ value.prescriptionDate }}
        </li>
        <li v-if="value.approvalDate">
          Approuvé le {{ value.approvalDate }}
        </li>
        <li v-if="!value.prescriptionDate || !value.approvalDate">
          &nbsp;
        </li>
        <li v-if="!value.prescriptionDate && !value.approvalDate">
          &nbsp;
        </li>
      </DUList>
    </DUGroup>
    <DUGroup
      v-if="value.topics.length"
      start
      xxs
    >
      <DUGroup
        horizontal
        xs
      >
        <DUHeading :level="5">
          Objet
        </DUHeading>
        <DUTag
          v-for="topic, index in value.topics"
          :key="index"
        >
          {{ topic }}
        </DUTag>
      </DUGroup>
      <DUText
        v-if="value.topicDetails"
        :rows="3"
        :value="value.topicDetails"
      />
    </DUGroup>
  </DUCard>
</template>
