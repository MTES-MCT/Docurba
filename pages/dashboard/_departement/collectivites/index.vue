<template>
  <v-container>
    <v-row>
      <v-col cols="12">
        <h1>Tableau de bord {{ $route.params.departement }}</h1>
      </v-col>
      <v-col cols="12">
        <v-tabs>
          <v-tab>Collectivités porteuses</v-tab>
          <v-tab>Collectivités non porteuses</v-tab>
        </v-tabs>
        <v-data-table
          :headers="headers"
          :items="desserts"
          item-key="name"
          class="elevation-1"
          :search="search"
        >
          <template #top>
            <v-text-field
              v-model="search"
              label="Rechercher"
              class="mx-4"
            />
          </template>
          <!-- eslint-disable-next-line -->
            <template #item.actions="{ item }">
            <div>
              <v-btn depressed color="primary" :to="{name:'dashboard-departement-collectivites-collectiviteId', params:{departement: $route.params.departement, collectiviteId: $route.params.departement }}">
                Consulter
              </v-btn>
              <v-btn depressed color="primary" :to="{name:'dashboard-departement-collectivites-collectiviteId', params:{departement: '47', collectiviteId:'LUL' }}">
                Voir FRP
              </v-btn>
            </div>
          </template>
        </v-data-table>
      </v-col>
    </v-row>
  </v-container>
</template>

<script>
export default {
  data () {
    return {
      search: '',
      calories: '',
      desserts: [
        {
          name: 'Frozen Yogurt',
          calories: 159,
          fat: 6.0,
          carbs: 24,
          protein: 4.0,
          iron: 1
        },
        {
          name: 'Ice cream sandwich',
          calories: 237,
          fat: 9.0,
          carbs: 37,
          protein: 4.3,
          iron: 1
        },
        {
          name: 'Eclair',
          calories: 262,
          fat: 16.0,
          carbs: 23,
          protein: 6.0,
          iron: 7
        },
        {
          name: 'Cupcake',
          calories: 305,
          fat: 3.7,
          carbs: 67,
          protein: 4.3,
          iron: 8
        },
        {
          name: 'Gingerbread',
          calories: 356,
          fat: 16.0,
          carbs: 49,
          protein: 3.9,
          iron: 16
        },
        {
          name: 'Jelly bean',
          calories: 375,
          fat: 0.0,
          carbs: 94,
          protein: 0.0,
          iron: 0
        },
        {
          name: 'Lollipop',
          calories: 392,
          fat: 0.2,
          carbs: 98,
          protein: 0,
          iron: 2
        },
        {
          name: 'Honeycomb',
          calories: 408,
          fat: 3.2,
          carbs: 87,
          protein: 6.5,
          iron: 45
        },
        {
          name: 'Donut',
          calories: 452,
          fat: 25.0,
          carbs: 51,
          protein: 4.9,
          iron: 22
        },
        {
          name: 'KitKat',
          calories: 518,
          fat: 26.0,
          carbs: 65,
          protein: 7,
          iron: 6
        }
      ]
    }
  },
  computed: {
    headers () {
      return [
        {
          text: 'Dessert (100g serving)',
          align: 'start',
          sortable: false,
          value: 'name'
        },
        {
          text: 'Calories',
          value: 'calories',
          filter: (value) => {
            if (!this.calories) { return true }

            return value < parseInt(this.calories)
          }
        },
        { text: 'Nom', value: 'fat' },
        { text: 'Type', value: 'carbs' },
        { text: 'Dernière proc. princip.', value: 'protein' },
        { text: 'Statut', value: 'iron' },
        { text: 'Actions', value: 'actions' }
      ]
    }
  }
}
</script>
