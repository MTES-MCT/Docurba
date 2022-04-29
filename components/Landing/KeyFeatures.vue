<template>
  <v-container>
    <v-row class="mt-16" justify="center" align="center">
      <v-col cols="12" sm="12" md="12">
        <h2 class="text-h2">
          Les atouts de Docurba
        </h2>
      </v-col>
      <v-col cols="12" sm="12" md="12">
        <v-list>
          <v-list-item>
            <v-list-item-avatar tile size="120">
              <v-img contain :src="require('@/assets/picto/undraw_cloud_files.svg')" />
              <!-- <v-sheet color="g300" width="120" height="120" /> -->
            </v-list-item-avatar>

            <v-divider vertical class="rm-divider mr-3 my-2 rm500" />

            <v-list-item-content>
              <v-list-item-title class="text-h3">
                Direct
              </v-list-item-title>
              <b>Ressources disponibles immédiatement.</b>
              Les éléments nationaux et régionaux, ainsi que les données concernant votre territoire sont mis à votre disposition par les services de l’Etat et téléchargeables aux formats .csv ou .shp.
            </v-list-item-content>
          </v-list-item>
          <v-list-item>
            <v-list-item-avatar tile size="120">
              <v-img contain :src="require('@/assets/picto/undraw_wireframing.svg')" />
              <v-sheet color="g300" width="120" height="120" />
            </v-list-item-avatar>

            <v-divider vertical class="rm-divider mr-3 my-2 rm500" />

            <v-list-item-content>
              <v-list-item-title class="text-h3">
                Lisible
              </v-list-item-title>
              <b>Navigation optimisée dans votre porter-à-connaissance.</b>
              Les données et informations du PAC sont mises en forme et faciles à consulter grâce à différents niveaux d’informations, et des fonctionnalités de commentaires ou partages au sein de l’équipe.
            </v-list-item-content>
          </v-list-item>
          <v-list-item>
            <v-list-item-avatar tile size="120">
              <v-img contain :src="require('@/assets/picto/undraw_collaboration.svg')" />
              <v-sheet color="g300" width="120" height="120" />
            </v-list-item-avatar>

            <v-divider vertical class="rm-divider mr-3 my-2 rm500" />

            <v-list-item-content>
              <v-list-item-title class="text-h3">
                Collaboratif
              </v-list-item-title>
              <b>Accompagnement des services de l’Etat.</b>
              La plateforme propose une FAQ dédiée, et l’option feuille de route partagée avec la possibilité de suivre les étapes clés de la procédure. Vous pouvez ainsi offrir de la visibilité aux Services de l’Etat, et aux parties prenantes associées lors de l’élaboration du document d’urbanisme.
            </v-list-item-content>
          </v-list-item>
          <v-list-item>
            <v-list-item-avatar tile size="120">
              <v-img contain :src="require('@/assets/picto/undraw_done_checking.svg')" />
              <v-sheet color="g300" width="120" height="120" />
            </v-list-item-avatar>

            <v-divider vertical class="rm-divider mr-3 my-2 rm500" />

            <v-list-item-content>
              <v-list-item-title class="text-h3">
                Complet
              </v-list-item-title>
              <b>Un maximum d’informations centralisées au même endroit.</b>
              supra-territoriaux (SRADDET, SCoT…), les données et le porter à connaissance préparé par la DGALN (Direction Générale de l’Aménagement du Territoire) en partenariat avec les DREAL et DDT (Direction Départementale du Territoire)
            </v-list-item-content>
          </v-list-item>
        </v-list>
      </v-col>
    </v-row>
  </v-container>
</template>
