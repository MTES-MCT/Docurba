<template>
  <v-container class="landing-container">
    <header class="hero-section">
      <h1 class="text-center">
        Loi Climat & Résilience
      </h1>
      <p>Faciliter son intégration dans vos documents d’urbanisme avec Docurba</p>

      <div class="search">
        <p>Pour commencer, accédez aux ressources de votre territoire :</p>
        <LandingSearchForm />
      </div>
    </header>
    <v-row align="center" justify="center" justify-md="start" class="landing-header">
      <v-col cols="12" sm="8" md="6">
        <h5 class="text-h5 text-bold">
          Collectivités
        </h5>
        <h1 class="landing-title">
          Sécurisez vos <LandingWordSlider />
        </h1>
        <p>
          Docurba centralise les ressources et échéances clés pour que vous soyez certains de ne jamais rater une étape ou une réglementation.
        </p>
        <v-btn color="primary" depressed :to="'/login/collectivites/signup'">
          S'inscrire
        </v-btn>
      </v-col>
      <img class="hero-img hidden-sm-and-down" src="/images/landing/loi_climat_hero.png">
    </v-row>
    <v-row>
      <v-col cols="12">
        <LandingCard
          img-src="/images/landing/loi_climat_card_1.png"
          title="Des procédures sécurisées"
          text="Consultez les règlementations et les données spécifiques à votre territoire dès le début de votre procédure."
          color="yellow"
        />
      </v-col>
    </v-row>
    <v-row>
      <v-col cols="12">
        <LandingCard
          img-src="/images/landing/loi_climat_card_2.png"
          img-side="left"
          title="Des procédures encadrées"
          text="Accédez à un support d'accompagnement structuré pour ne jamais passer à côté d'une étape ou d'un événement obligatoire dans votre procédure."
          color="blue"
        />
      </v-col>
    </v-row>
    <v-row>
      <v-col cols="12" md="6">
        <LandingCard
          class="fill-height"
          title="Des procédures collaboratives"
          text="Collaborez avec tous les acteurs de votre procédure et formalisez ainsi vos échanges : bureaux d'études, services de l'état, personnes publiques associées, ..."
        />
      </v-col>
      <v-col cols="12" md="6">
        <LandingCard
          class="fill-height"
          title="Pour toutes vos procédures d’urbanisme"
          text="Docurba vous accompagne dans l’élaboration de vos PLU, PLUi, SCOT, et Cartes Communales."
        />
      </v-col>
    </v-row>
    <v-row>
      <v-col>
        <LandingCard>
          <v-row justify="center">
            <v-col cols="12" md="10" class="text-center">
              <h2>
                Inscrivez-vous pour débuter
              </h2>
              <p>
                Créez votre compte sur Docurba pour éditer vos procédures ou Porter à Connaissance et accélérer vos projets d'urbanisme dès maintenant.
              </p>
              <v-btn color="primary" :to="'/login'" depressed>
                S'inscrire
              </v-btn>
            </v-col>
          </v-row>
        </LandingCard>
      </v-col>
    </v-row>
  </v-container>
</template>

<style scoped>
h1 {
  font-size: 3.5rem;
  font-weight: 700;
  line-height: 64px;
}

.hero-section {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 3.5rem;
  padding: 6.5rem 0;
}

.search {
  width: 100%;
  max-width: 960px;
  padding: 2.5rem 3rem;
  border: 1px solid #DDDDDD;
  border-radius: 0.5rem;
  background-color: #F9F8F6;
}

.search > p {
  font-size: 18px;
  font-weight: 700;
}

.landing-container {
  display: flex;
  flex-direction: column;
  gap: 2.5rem;
}

.landing-title {
  font-size: 3.5rem;
  font-weight: 700;
  line-height: 64px;
}

.landing-header {
  height: 728px;
}

.hero-img {
  position: absolute;
  right: 82px;
  height: auto;
  max-height: 628px;
  max-width: 50%;
}
</style>
