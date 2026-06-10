<script setup lang="ts">
import { computed, ref } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import BaseActionable from '@/components/BaseActionable.vue'
import FrButton from '@/components/FrButton.vue'
import FrFooter from '@/components/FrFooter.vue'
import FrHeader from '@/components/FrHeader.vue'
import FrMenu from '@/components/FrMenu.vue'
import FrNotice from '@/components/FrNotice.vue'
import { useAuth } from '@/composables/useAuth'
import type { Options } from '@/data/Option'

const accountOptions: Options<() => void> = [{
  label: 'Me déconnecter',
  value: signOutAndRedirect,
}]
const documentationOptions: Options<string> = [{
  label: 'Guide d\'utilisation',
  value: 'https://docurba.crisp.help/fr/category/ressources-1jtg3x2/',
}, {
  label: 'FAQ',
  value: 'https://docurba.crisp.help/fr/',
}, {
  label: 'Webinaires',
  value: 'https://docurba.crisp.help/fr/category/ressources-1jtg3x2/',
}, {
  label: 'Contact',
  value: 'https://docurba.crisp.help/fr/category/nous-contacter-cf4bsp/',
}, {
  label: 'API',
  value: '/api',
}]
const solutionOptions: Options<string> = [{
  label: 'Docurba pour :',
  options: [{
    label: 'Les Collectivités',
    value: '/collectivites',
  }, {
    label: 'Les Bureaux d\'Étude',
    value: '/bureaux-d-etudes',
  }, {
    label: 'Les Services de l\'État',
    value: '/services-de-l-etat',
  }],
}]

const noticeDismissed = ref(false)

const { signedIn, signOut, user } = useAuth()
const route = useRoute()
const router = useRouter()

const noticeVisible = computed<boolean>(() =>
  !signedIn.value
  && !route.path.startsWith('/connexion')
  && !noticeDismissed.value
)

async function signOutAndRedirect() {
  await signOut()

  if (signedIn.value || route.path === '/') return

  router.push('/')
}
</script>

<template>
  <FrHeader>
    <template #service>Docurba</template>
    <template #tools>
      <FrButton v-if="signedIn"
                sm
                to="/tableau-de-bord">Tableau de bord</FrButton>
      <FrMenu v-else
              :options="solutionOptions"
              sm>Solutions</FrMenu>
      <FrMenu :options="documentationOptions"
              sm>Documentation</FrMenu>
      <FrMenu v-if="user"
              :options="accountOptions"
              sm>
        <template #trigger="{ active, className, close, ref, toggle }">
          <FrButton :active="active"
                    class="fr-icon--before fr-icon--before-account-circle-fill"
                    :class="className"
                    :ref="ref?.name"
                    sm
                    tertiary-borderless
                    @actuated="toggle()"
                    @keydown.esc="close">{{ user.firstname }}</FrButton>
        </template>
      </FrMenu>
      <FrButton v-else
                class="fr-icon--before fr-icon--before-account-circle-fill"
                sm
                to="/connexion">Me connecter</FrButton>
    </template>
  </FrHeader>
  <FrNotice v-if="noticeVisible"
            @dismissed="noticeDismissed = true">
    <template #title>Vous représentez un territoire ou l'État ?</template>
    <template #default>Pour accéder à plus d'informations et suivre vos documents d'urbanisme, <BaseActionable to="/connexion">identifiez-vous</BaseActionable></template>
  </FrNotice>
  <RouterView />
  <FrFooter>
    <template #brand>
      Ministères<br />
      transition écologique<br />
      aménagement du territoire<br />
      transports<br />
      ville et logement
    </template>
    <template #default>
      <p class="fr-text fr-text--sm">Docurba centralise les ressources à chaque étape de vos procédures d'urbanisme pour plus de rapidité, une meilleure conformité et une visibilité en temps réel.</p>
      <p class="fr-text fr-text--sm">Le <BaseActionable to="https://github.com/MTES-MCT/Docurba">code source</BaseActionable> est ouvert et les contributions bienvenues.</p>
    </template>
  </FrFooter>
</template>
