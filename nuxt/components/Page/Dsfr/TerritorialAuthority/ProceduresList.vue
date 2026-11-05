<script>
import { mdiArrowRight, mdiLock } from '@mdi/js'
import { displayDate } from '~/plugins/utils'

export default {
  props: {
    value: {
      default: () => [],
      type: Array,
    },
  },
  data() {
    return {
      icons: {
        mdiArrowRight,
        mdiLock,
      },
    }
  },
  computed: {
    activeIds() {
      return this.$route.query.details
        ? this.$route.query.details.split(',')
        : []
    },
    activeSecondaryIds() {
      return this.$route.query.secondaires
        ? this.$route.query.secondaires.split(',')
        : []
    },
    displayedProcedures() {
      return this.value.map((procedure) => ({
        approvalDate: displayDate(procedure.approvalDate),
        comment: procedure.comment ?? '',
        id: procedure.id,
        lastEvent: procedure.lastEvent
          ? {
            date: displayDate(procedure.lastEvent.date),
            type: procedure.lastEvent.type ?? '',
          }
          : null,
        lastStructuringtEvent: procedure.lastStructuringtEvent
          ? {
            date: displayDate(procedure.lastStructuringtEvent.date),
            type: procedure.lastStructuringtEvent.type ?? '',
          }
          : null,
        name: procedure.name ?? '',
        prescriptionDate: displayDate(procedure.prescriptionDate),
        privateComment: procedure.privateComment ?? '',
        procedures: procedure.procedures.map((secondaryProcedure) => ({
          approvalDate: displayDate(secondaryProcedure.approvalDate),
          id: secondaryProcedure.id,
          name: secondaryProcedure.name ?? '',
          prescriptionDate: displayDate(secondaryProcedure.prescriptionDate),
          topicDetails: secondaryProcedure.topicDetails ?? '',
          topics: secondaryProcedure.topics,
        })),
        sudocuhId: procedure.sudocuhId ?? '',
        topicDetails: procedure.topicDetails ?? '',
        topics: procedure.topics,
        towns: procedure.towns,
      }))
    },
    perimeterId() {
      return this.$route.query.perimetre || null
    },
  },
  methods: {
    closePerimeter() {
      this.$router.push({
        query: {
          ...this.$route.query,
          perimetre: undefined,
        },
      })
    },
    setActive(id, value) {
      const index = this.activeIds.indexOf(id)

      if ((index === -1) === !value) return

      const activeIds = value
        ? [...this.activeIds, id]
        : [
          ...this.activeIds.slice(0, index),
          ...this.activeIds.slice(index + 1),
        ]

      this.$router.push({
        query: {
          ...this.$route.query,
          details: activeIds.length
            ? activeIds.join(',')
            : undefined,
        },
      })
    },
    setSecondaryActive(id, value) {
      const index = this.activeSecondaryIds.indexOf(id)

      if ((index === -1) === !value) return

      const activeSecondaryIds = value
        ? [...this.activeSecondaryIds, id]
        : [
          ...this.activeSecondaryIds.slice(0, index),
          ...this.activeSecondaryIds.slice(index + 1),
        ]

      this.$router.push({
        query: {
          ...this.$route.query,
          secondaires: activeSecondaryIds.length
            ? activeSecondaryIds.join(',')
            : undefined,
        },
      })
    },
  },
}
</script>

<template>
  <FRGrid gap="md lg-lg">
    <FRCollapsibleCard v-for="procedure in displayedProcedures"
                       :key="procedure.id"
                       :label="
                         procedure.procedures.length
                           ? `Déplier ${
                             procedure.procedures.length === 1
                               ? 'la procédure secondaire'
                               : `les ${procedure.procedures.length} procédures secondaires`
                           }`
                           : ''
                       "
                       :value="activeSecondaryIds.includes(procedure.id)"
                       @input="setSecondaryActive(procedure.id, $event)">
      <template #header>
        <FRGrid gap="md">

          <FRGrid gap="xs"
                  start>
            <DUProcedureStatus v-if="procedure.status"
                               sm
                               :value="procedure.status" />
            <FRGrid gap="xxs">
              <FRText h6
                      tag="h3">
                {{ procedure.name }}
              </FRText>
              <FRDottedList sm>
                <li v-if="procedure.prescriptionDate">
                  Prescrit le {{ procedure.prescriptionDate }}
                </li>
                <li v-if="procedure.approvalDate">
                  Approuvé le {{ procedure.approvalDate }}
                </li>
                <li v-if="procedure.lastStructuringtEvent">
                  Dernier événement clé le {{ procedure.lastStructuringtEvent.date }}&nbsp;:
                  <em>
                    {{ procedure.lastStructuringtEvent.type }}
                  </em>
                </li>
              </FRDottedList>
            </FRGrid>
          </FRGrid>
          <FRGrid v-if="procedure.topics.length || procedure.topicDetails"
                  gap="xxs">
            <FRGrid gap="xs"
                    horizontal>
              <FRText>
                Objet
              </FRText>
              <FRTag v-for="topic in procedure.topics"
                     :key="topic"
                     actionable-child>
                {{ topic }}
              </FRTag>
              <FRTag v-if="!procedure.topics.length"
                     actionable-child>
                Autre
              </FRTag>
            </FRGrid>
            <FRText v-if="procedure.topicDetails"
                    sm>
              {{ procedure.topicDetails }}
            </FRText>
          </FRGrid>
          <FRGrid v-if="procedure.comment"
                  gap="xxs">
            <FRText>
              Commentaire
            </FRText>
            <FRText :rows="2"
                    sm
                    :title="procedure.comment">
              {{ procedure.comment }}
            </FRText>
          </FRGrid>
          <FRGrid v-if="procedure.privateComment"
                  gap="xxs">
            <FRGrid gap="xs"
                    horizontal>
              <FRIcon md
                      :value="icons.mdiLock" />
              <FRText>
                Commentaire visible uniquement par la DDT
              </FRText>
            </FRGrid>
            <FRText :rows="2"
                    sm
                    :title="procedure.privateComment">
              {{ procedure.privateComment }}
            </FRText>
          </FRGrid>
          <FRAccordion label="Détails"
                       :value="activeIds.includes(procedure.id)"
                       @input="setActive(procedure.id, $event)">
            <FRGrid gap="md"
                    start>
              <FRText v-if="procedure.lastEvent"
                      sm>
                Dernier événement le {{ procedure.lastEvent.date }}&nbsp;:
                <em>
                  {{ procedure.lastEvent.type }}
                </em>
              </FRText>
              <FRLink sm
                      :to="{
                        query: {
                          ...$route.query,
                          perimetre: procedure.id,
                        },
                      }">
                Périmètre de la procédure&nbsp;: {{ procedure.towns.length }} commune{{ procedure.towns.length === 1 ? '' : 's' }}
              </FRLink>
              <FRModal v-if="procedure.id === perimeterId"
                       @closed="closePerimeter()">
                <FRGrid gap="xxs">
                  <FRText h4
                          light
                          tag="h4">
                    {{ procedure.name }}
                  </FRText>
                  <FRText h4>
                    Périmètre de la procédure&nbsp;: {{ procedure.towns.length }} commune{{ procedure.towns.length === 1 ? '' : 's' }}
                  </FRText>
                </FRGrid>
                <FRGrid gap="xs"
                        horizontal>
                  <FRLink v-for="town in procedure.towns"
                          :to="{
                            name: 'dsfr-collectivites-code_collectivite',
                            params: {
                              code_collectivite: town.code,
                            },
                            query: {
                              vue: $route.query.vue,
                            },
                          }">
                    {{ town.name }} ({{ town.code }})
                  </FRLink>
                </FRGrid>
              </FRModal>
              <FRDottedList sm>
                <li>
                  Identifiant de la procédure&nbsp;: {{ procedure.id }}
                </li>
                <li v-if="procedure.sudocuhId">
                  Sudocuh&nbsp;: {{ procedure.sudocuhId }}
                </li>
              </FRDottedList>
            </FRGrid>
          </FRAccordion>
          <FRGrid end>
            <FRLink :to="{
                      name: 'dsfr-procedures-id_procedure',
                      params: {
                        id_procedure: procedure.id,
                      },
                    }">
              Aller à la feuille de route
              <FRIcon :value="icons.mdiArrowRight" />
            </FRLink>
          </FRGrid>
        </FRGrid>
      </template>
      <template #default>
        <FRCard v-for="secondaryProcedure in procedure.procedures"
                :key="secondaryProcedure.id"
                raised
                :title="secondaryProcedure.name"
                :to="{
                  name: 'dsfr-procedures-id_procedure',
                  params: {
                    id_procedure: secondaryProcedure.id,
                  },
                }">
          <FRGrid gap="md">
            <FRGrid gap="xxs">
              <FRText display
                      :rows="1"
                      tag="h4">
                {{ secondaryProcedure.name }}
              </FRText>
              <FRGrid v-if="secondaryProcedure.approvalDate || secondaryProcedure.prescriptionDate">
                <FRText v-if="secondaryProcedure.prescriptionDate"
                        mention
                        xs>
                  Prescrit le {{ secondaryProcedure.prescriptionDate }}
                </FRText>
                <FRText v-if="secondaryProcedure.approvalDate"
                        mention
                        xs>
                  Approuvé le {{ secondaryProcedure.approvalDate }}
                </FRText>
              </FRGrid>
            </FRGrid>
            <FRGrid v-if="procedure.topics.length || procedure.topicDetails"
                    gap="xxs">
              <FRGrid gap="xs"
                      horizontal>
                <FRText>
                  Objet
                </FRText>
                <FRTag v-for="topic in procedure.topics"
                       :key="topic"
                       actionable-child>
                  {{ topic }}
                </FRTag>
                <FRTag v-if="!procedure.topics.length"
                       actionable-child>
                  Autre
                </FRTag>
              </FRGrid>
              <FRText v-if="procedure.topicDetails"
                      sm>
                {{ procedure.topicDetails }}
              </FRText>
            </FRGrid>
          </FRGrid>
        </FRCard>
      </template>
    </FRCollapsibleCard>
  </FRGrid>
</template>
