<template>
  <v-container>
    <!-- User stories -->
    <v-row class="py-16">
      <v-col cols="12">
        <h2 class="text-h2">
          Comment ça marche?
        </h2>
      </v-col>
    </v-row>
    <v-row justify="space-around" align="center">
      <v-col cols="12" sm="6" md="3" lg="3">
        <v-card flat height="320" color="g100">
          <v-row justify="center">
            <v-col cols="10">
              <v-img height="150px" contain :src="require('@/assets/picto/undraw_search.svg')" />
              <!-- <v-sheet height="200" width="200" color="g300" /> -->
            </v-col>
          </v-row>
          <v-row>
            <v-col>
              <v-card-text>
                <b>Je précise mon territoire</b> et le type de document d’urbanisme
              </v-card-text>
            </v-col>
          </v-row>
        </v-card>
      </v-col>
      <v-col cols="12" sm="6" md="3" lg="3">
        <v-card flat height="320" color="g100">
          <v-row justify="center">
            <v-col cols="10">
              <v-img height="150px" contain :src="require('@/assets/picto/undraw_file_analysis.svg')" />
              <!-- <v-sheet height="200" width="200" color="g300" /> -->
            </v-col>
          </v-row>
          <v-row>
            <v-col>
              <v-card-text>
                <b>J’accède aux premiers éléments</b> fournis par les Services de l’Etat pour mon département
              </v-card-text>
            </v-col>
          </v-row>
        </v-card>
      </v-col>
      <v-col cols="12" sm="6" md="3" lg="3">
        <v-card flat height="320" color="g100">
          <v-row justify="center">
            <v-col cols="10">
              <v-img height="150px" contain :src="require('@/assets/picto/undraw_profile.svg')" />
              <!-- <v-sheet height="200" width="200" color="g300" /> -->
            </v-col>
          </v-row>
          <v-row>
            <v-col>
              <v-card-text>
                <b>Je crée un compte</b>
                et demande mon PAC à ma DDT
                (Direction Départementale des Territoires)
              </v-card-text>
            </v-col>
          </v-row>
        </v-card>
      </v-col>
      <v-col cols="12" sm="6" md="3" lg="3">
        <v-card flat height="320" color="g100">
          <v-row justify="center">
            <v-col cols="10">
              <v-img height="150px" contain :src="require('@/assets/picto/undraw_message_sent.svg')" />
              <!-- <v-sheet height="200" width="200" color="g300" /> -->
            </v-col>
          </v-row>
          <v-row>
            <v-col>
              <v-card-text>
                <b>Je reçois mon PAC en ligne,</b>
                ma note d’enjeux le cas échéant,
                et un accompagnement du projet
              </v-card-text>
            </v-col>
          </v-row>
        </v-card>
      </v-col>
    </v-row>
  </v-container>
</template>
