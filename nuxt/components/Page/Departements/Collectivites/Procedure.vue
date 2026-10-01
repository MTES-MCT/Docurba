<script>
import { mdiArrowRight, mdiLock } from '@mdi/js'

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
        mdiArrowRight,
        mdiLock
      }
    }
  },
  computed: {
    departmentCode () {
      return this.$route.params.code_departement?.padStart(2, '0') || null
    },
    detailsActive: {
      get () {
        return this.detailsActiveIds.includes(this.value.id)
      },
      set (newValue) {
        if (newValue === this.detailsActiveIds.includes(this.value.id)) {
          return
        }
        if (newValue) {
          this.$router.push({
            ...this.$route,
            query: {
              ...this.$route.query,
              details_procedures: [
                ...this.detailsActiveIds,
                this.value.id
              ].join(',')
            }
          })
        } else {
          const index = this.detailsActiveIds.indexOf(this.value.id)

          this.$router.push({
            ...this.$route,
            query: {
              ...this.$route.query,
              details_procedures: this.detailsActiveIds.length === 1
                ? undefined
                : [
                    ...this.detailsActiveIds.slice(0, index),
                    ...this.detailsActiveIds.slice(index + 1)
                  ].join(',')
            }
          })
        }
      }
    },
    detailsActiveIds () {
      return this.$route.query.details_procedures
        ? this.$route.query.details_procedures.split(',')
        : []
    },
    dialogActive: {
      get () {
        return this.$route.query.perimetre_procedure === this.value.id
      },
      set (newValue) {
        this.$router.push({
          query: {
            ...this.$route.query,
            perimetre_procedure: newValue ? this.value.id : undefined
          }
        })
      }
    },
    privateCommentAvailable () {
      return !!this.value.privateComment && this.$user.canViewProcedureCommentFromSudocuh()
    },
    secondariesActive: {
      get () {
        return this.secondariesActiveIds.includes(this.value.id)
      },
      set (newValue) {
        if (newValue === this.secondariesActiveIds.includes(this.value.id)) {
          return
        }
        if (newValue) {
          this.$router.push({
            ...this.$route,
            query: {
              ...this.$route.query,
              procedures_secondaires: [
                ...this.secondariesActiveIds,
                this.value.id
              ].join(',')
            }
          })
        } else {
          const index = this.secondariesActiveIds.indexOf(this.value.id)

          this.$router.push({
            ...this.$route,
            query: {
              ...this.$route.query,
              procedures_secondaires: this.secondariesActiveIds.length === 1
                ? undefined
                : [
                    ...this.secondariesActiveIds.slice(0, index),
                    ...this.secondariesActiveIds.slice(index + 1)
                  ].join(',')
            }
          })
        }
      }
    },
    secondariesActiveIds () {
      return this.$route.query.procedures_secondaires
        ? this.$route.query.procedures_secondaires.split(',')
        : []
    },
    sudocuhCommentAvailable () {
      return !!this.value.sudocuhComment && this.$user.canViewProcedureCommentFromSudocuh()
    },
    territorialAuthorityCode () {
      return this.$route.params.code_collectivite || null
    }
  }
}
</script>

<template>
  <DUCollapsibleCard
    v-model="secondariesActive"
    :disabled="!value.procedures.length"
    :label="`Déplier ${
      value.procedures.length === 1
        ? 'la procédure secondaire'
        : `les ${value.procedures.length} procédures secondaires`
    }`"
  >
    <template #header>
      <DUGroup
        start
        xs
      >
        <ProcedureStatus
          v-if="value.status"
          :value="value.status"
        />
        <DUGroup
          start
          xxs
        >
          <DUHeading
            :level="3"
            strong
          >
            {{ value.name }}
          </DUHeading>
          <DUDottedList sm>
            <li v-if="value.prescriptionDate">
              Prescrit le {{ value.prescriptionDate }}
            </li>
            <li v-if="value.approvalDate">
              Approuvé le {{ value.approvalDate }}
            </li>
            <li v-if="value.lastStructuringEventDate">
              Dernier événement clé le {{ value.lastStructuringEventDate }}&nbsp;:<em>&nbsp;{{ value.lastStructuringEventType }}</em>
            </li>
          </DUDottedList>
        </DUGroup>
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
          <DUHeading :level="4">
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
      <DUGroup
        v-if="value.comment"
        xxs
      >
        <DUHeading :level="4">
          Commentaire
        </DUHeading>
        <DUText
          :rows="2"
          :value="value.comment"
        />
      </DUGroup>
      <DUGroup
        v-if="privateCommentAvailable"
        xxs
      >
        <DUGroup
          horizontal
          start
          xs
        >
          <VIcon small>
            {{ icons.mdiLock }}
          </VIcon>
          <DUHeading :level="4">
            Commentaire visible uniquement par la DDT
          </DUHeading>
        </DUGroup>
        <DUText
          :rows="2"
          :value="value.privateComment"
        />
      </DUGroup>
      <DUGroup
        v-if="sudocuhCommentAvailable"
        xxs
      >
        <DUGroup
          horizontal
          start
          xs
        >
          <VIcon small>
            {{ icons.mdiLock }}
          </VIcon>
          <DUHeading :level="4">
            Commentaire provenant de Sudocuh visible uniquement par la DDT
          </DUHeading>
        </DUGroup>
        <DUText
          :rows="2"
          :value="value.sudocuhComment"
        />
      </DUGroup>
      <DUCollapsible
        v-model="detailsActive"
        label="Détails"
      >
        <DUGroup
          md
          start
        >
          <DUText v-if="value.lastEventDate">
            Dernier événement le {{ value.lastEventDate }}&nbsp;:<em>&nbsp;{{ value.lastEventType }}</em>
          </DUText>
          <DULink @actuated="dialogActive = true">
            Périmètre de la procédure&nbsp;: {{ value.towns.length }} commune{{ value.towns.length === 1 ? '' : 's' }}
          </DULink>
          <DUDialog v-model="dialogActive">
            <DUHeading :level="3">
              <div>{{ value.name }}</div>
              <div>
                <strong>Périmètre de la procédure&nbsp;: {{ value.towns.length }} commune{{ value.towns.length === 1 ? '' : 's' }}</strong>
              </div>
            </DUHeading>
            <DULinksList>
              <DULink
                v-for="town in value.towns"
                :key="town.code"
                :to="{
                  params: {
                    code_collectivite: town.code,
                    code_departement: departmentCode
                  },
                  query: {
                    vue: $route.query.vue
                  }
                }"
              >
                {{ town.name }} ({{ town.code }})
              </DULink>
            </DULinksList>
          </DUDialog>
          <DUDottedList sm>
            <li>Identifiant de la procédure&nbsp;: {{ value.id }}</li>
            <li v-if="value.sudocuhId">
              sudocuh&nbsp;: {{ value.sudocuhId }}
            </li>
            <li v-if="value.parentId">
              parent&nbsp;: {{ value.parentId }}
            </li>
          </DUDottedList>
        </DUGroup>
      </DUCollapsible>
      <DUGroup end>
        <DULink
          :to="{
            name: 'departements-code_departement-collectivites-code_collectivite-procedures-id_procedure',
            params: {
              code_collectivite: territorialAuthorityCode,
              code_departement: departmentCode,
              id_procedure: value.id
            }
          }"
        >
          Aller à la feuille de route
          <VIcon small>
            {{ icons.mdiArrowRight }}
          </VIcon>
        </DULink>
      </DUGroup>
    </template>
    <template
      v-if="value.procedures.length"
      #default
    >
      <PageDepartementsCollectivitesSecondaryProcedure
        v-for="procedure in value.procedures"
        :key="procedure.id"
        :value="procedure"
      />
    </template>
  </DUCollapsibleCard>
</template>
