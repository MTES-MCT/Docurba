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
  }
}
</script>

<template>
  <DUCard :to="`/frise/${value.id}`">
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
