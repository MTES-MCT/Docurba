<script setup lang="ts">
import BaseActionable from '@/components/BaseActionable.vue'
import FrButton from '@/components/FrButton.vue'
import FrCard from '@/components/FrCard.vue'
import FrContainer from '@/components/FrContainer.vue'

// Definitions
definePage({
  meta: {
    signedOutOnly: true,
  },
})
</script>

<template>
  <FrContainer id="content"
               role="main"
               tag="main"
               vertical>
    <h1 class="fr-text fr-text--h1">Inscription et connexion</h1>
    <p class="fr-text">Les données publiques de Docurba sont accessibles librement, sans compte, en naviguant sur le site ou en consultant notre <BaseActionable to="/dev/api">API</BaseActionable>.</p>
    <p class="fr-text">La création de compte Docurba est réservée aux acteurs de la planification pour contribuer notamment au suivi de leurs documents d'urbanisme en cours d'élaboration.</p>
    <h2 class="fr-text fr-text--h2">Vous représentez...</h2>
    <div class="fr-row">
      <div class="fr-col-12 fr-col-md">
        <FrCard>
          <template #title>Les territoires</template>
          <template #default>
            <p class="fr-text fr-text--sm">Vous êtes un élu, un technicien ou employé d'une collectivité, bureau d'étude ou agence d'urbanisme. Accédez simplement aux informations relatives à l'élaboration ou l'évolution de vos documents d'urbanisme.</p>
            <p class="fr-text fr-text--sm">Après vérification de votre accès, vous pourrez naviguer dans votre espace personnalisé.</p>
          </template>
          <template #footer>
            <FrButton secondary
                      to="/connexion/collectivite">Me connecter</FrButton>
            <FrButton to="/connexion/collectivite/creation">Créer un compte territoires</FrButton>
          </template>
        </FrCard>
      </div>
      <div class="fr-col--center fr-col-12 fr-col-md-1">
        <p class="fr-text fr-text--center">ou</p>
      </div>
      <div class="fr-col-12 fr-col-md">
        <FrCard>
          <template #title>Les services de l'État</template>
          <template #default>
            <p class="fr-text fr-text--sm">Vous êtes un agent d'une DDT(M)/DEAL ou d'une DREAL en charge du suivi des procédures d'élaboration et d'évolution des documents d'urbanisme et/ou de la production des documents de l'État liés à ces procédures (PAC, etc.).</p>
            <p class="fr-text fr-text--sm">Après vérification de votre accès, vous pourrez paramétrer votre trame de PAC départementale ou régionale, et suivre vos procédures.</p>
          </template>
          <template #footer>
            <FrButton secondary
                      to="/connexion/etat">Me connecter</FrButton>
            <FrButton to="/connexion/etat/creation">Créer un compte agent de l'État</FrButton>
          </template>
        </FrCard>
      </div>
    </div>
  </FrContainer>
</template>
