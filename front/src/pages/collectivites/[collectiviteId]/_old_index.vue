<script setup lang="ts">
import { computed } from 'vue';
import { useRoute } from 'vue-router'
import FrBreadcrumbs from '@/components/FrBreadcrumbs.vue'
import FrContainer from '@/components/FrContainer.vue'
import FrTabs from '@/components/FrTabs.vue'
import FrTile from '@/components/FrTile.vue'
import { useCollectivite } from '@/composables/useCollectivite'
import { useRouteQueryParam } from '@/composables/useRouteQueryParam'
import type { Option } from '@/data/Option'

// Route
const route = useRoute()

const tab = useRouteQueryParam<string | null>('tab')

const collectiviteId = computed<string>(() => String(route.params.collectiviteId))

// Data
const { collectivite } = useCollectivite(collectiviteId)

// View
const tabOptions: Array<Option<string>> = [{
  label: 'DU intercommunaux',
  value: 'du-intercommunaux',
}, {
  label: 'DU communaux',
  value: 'du-communaux',
}, {
  label: 'SCoT',
  value: 'scot',
}]

const breadcrumbs = computed<Array<Option<string>>>(() => collectivite.value ? [{
  label: `Mes collectivités (${collectivite.value.departementId})`,
  value: `/departements/${collectivite.value.departementId}`
}] : [])
</script>

<template>
  <FrContainer v-if="collectivite"
               id="content"
               role="main"
               tag="main"
               vertical>
    <FrBreadcrumbs :value="breadcrumbs">{{ collectivite.name }}</FrBreadcrumbs>
    <h1 class="fr-text fr-text--h1">{{ collectivite.name }} ({{ collectivite.id }})</h1>
    <h2 class="fr-text fr-text--h4">Actions rapides</h2>
    <div class="fr-row">
      <div class="fr-col-12 fr-col-sm-6 fr-col-lg-3">
        <FrTile to="/connexion">
          <template #title>Nouvelle procédure</template>
          <template #description>Démarrez une nouvelle procédure de document d'urbanisme.</template>
        </FrTile>
      </div>
      <div class="fr-col-12 fr-col-sm-6 fr-col-lg-3">
        <FrTile :to="`/collectivites/${collectiviteId}/pac`">
          <template #title>Socle de Porter à connaissance</template>
          <template #description>Consultez votre socle de Porter à Connaissance.</template>
        </FrTile>
      </div>
      <div class="fr-col-12 fr-col-sm-6 fr-col-lg-3">
        <FrTile :to="`/collectivites/${collectiviteId}/ressources`">
          <template #title>Ressources</template>
          <template #description>Consultez des ressources autour de vos documents d’urbanisme.</template>
        </FrTile>
      </div>
      <div class="fr-col-12 fr-col-sm-6 fr-col-lg-3">
        <FrTile :to="`/collectivites/${collectiviteId}/donnees`">
          <template #title>Données</template>
          <template #description>Consultez les données de votre territoire.</template>
        </FrTile>
      </div>
    </div>
    <h2 class="fr-text fr-text--h4">Documents d'urbanisme</h2>
    <p class="fr-text">Documents d'urbanisme disponibles pour la collectivité recherchée :</p>
    <FrTabs :options="tabOptions"
            v-model:value="tab">
      <p class="fr-text">DU intercommunaux</p>
      <p class="fr-text">DU communaux</p>
      <p class="fr-text">SCoT</p>
    </FrTabs>
  </FrContainer>
</template>
