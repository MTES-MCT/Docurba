<template>
  <v-container>
    <v-row>
      <v-col cols="12">
        <h1>Une Commune {{ $route.params.departement }}</h1>
      </v-col>
      <v-col cols="12">
        <v-expansion-panels flat>
          <v-expansion-panel class="beige">
            <v-expansion-panel-header>
              <h3>11 communes dans votre EPCI</h3>
            </v-expansion-panel-header>
            <v-expansion-panel-content>
              <v-container>
                <v-row>
                  <v-col
                    v-for="(item,i) in 5"
                    :key="i"
                    cols="4"
                    class="pt-0 pl-0"
                  >
                    Labelou
                    <v-divider class="mt-3" />
                  </v-col>
                </v-row>
              </v-container>
            </v-expansion-panel-content>
          </v-expansion-panel>
        </v-expansion-panels>
      </v-col>
    </v-row>
    <v-row>
      <v-col cols="12">
        <h2>Documents d'urbanisme</h2>
        <p>
          Documents d’urbanismes disponibles pour la commune recherchée :
        </p>
      </v-col>
      <v-col cols="12">
        <DashboardDUItem
          v-for="(item,i) in 5"
          :key="'du_' + i"
        />
      </v-col>
    </v-row>
  </v-container>
</template>
