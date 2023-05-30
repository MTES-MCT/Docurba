<template>
  <v-card flat color="bf100-g750" class="position-relative">
    <VFloatingShape src="/images/landing/circle_light_yellow.svg" :size="80" :right="10" :bottom="-24" />
    <v-card-title>
      <v-row no-gutters>
        <v-col cols="12">
          <v-icon color="focus">
            {{ icons.mdiInformationOutline }}
          </v-icon>
        </v-col>
        <v-col>
          <b>Qu'est ce qu'un PAC ?</b>
        </v-col>
      </v-row>
    </v-card-title>
    <v-card-text class="black--text">
      <p>Le PAC contient les informations nécessaires à l’exercice des compétences des collectivités en matière d’urbanisme. Il contient notamment le cadre législatif et réglementaire à respecter ou encore les protections existantes en matière d’environnement et de patrimoine sur le territoire.</p>
      <p class="font-weight-bold">
        Consultez un exemple de socle de PAC déjà disponible
      </p>
      <nuxt-link :to="{path:'/collectivites/1006/pac', query:{isEpci: false, document:'PLU'}}" class="primary--text text-decoration-underline">
        <v-icon small color="primary">
          {{ icons.mdiArrowRight }}
        </v-icon>
        Région Auvergne-Rhône-Alpes
      </nuxt-link>
    </v-card-text>
  </v-card>
</template>

<script>
import { mdiInformationOutline, mdiArrowRight } from '@mdi/js'
export default {
  data () {
    return {
      icons: {
        mdiInformationOutline,
        mdiArrowRight
      }
    }
  }
}
</script>
