<template>
  <v-container class="py-0">
    <v-timeline dense align-top>
      <v-timeline-item>
        <v-row class="pt-1">
          <v-col cosl="12" sm="3" md="2">
            11/06/1993
          </v-col>
          <v-col cols="12" sm="9" md="10">
            <v-card>
              <v-card-title>
                Titre de la news
              </v-card-title>
              <v-card-text>
                Lorem ipsum dolor sit amet, consectetur adipisicing elit. Dignissimos, totam consequatur facilis aliquid voluptas omnis laborum sint eius ullam atque distinctio earum voluptates minus architecto magni deleniti nihil quae tempore?
                Lorem ipsum dolor, sit amet consectetur adipisicing elit. Animi, porro quod? Voluptatum possimus veritatis nostrum distinctio voluptas tenetur, saepe laborum quaerat quibusdam ipsum quae inventore culpa dolor animi architecto consectetur.
                Lorem ipsum dolor sit amet consectetur adipisicing elit. Voluptates fugiat soluta incidunt. Sit iusto adipisci ratione doloremque quos, perferendis exercitationem quis maxime quasi? Maxime harum voluptas nesciunt dolores ex possimus.
              </v-card-text>
              <v-card-actions>
                <v-btn block color="primary" href="/news/item" nuxt>
                  Voir plus
                </v-btn>
              </v-card-actions>
            </v-card>
          </v-col>
        </v-row>
      </v-timeline-item>
    </v-timeline>
  </v-container>
</template>

<script>
export default {
  async asyncData ({ $content }) {
    const FAQ = await $content('FAQ', {
      deep: true
    }).fetch()

    return {
      FAQ: FAQ.filter(q => q.visible)
    }
  }
}
</script>
