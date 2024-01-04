<template>
  <div class="landing-container">
    <main class="landing">
      <header class="hero-section">
        <h1 class="text-center">
          Docurba vous accompagne dans l'élaboration de vos <LandingWordSlider />
        </h1>

        <div class="search">
          <p>Pour commencer, accédez aux ressources de votre territoire :</p>
          <LandingSearchForm />
        </div>
      </header>

      <div class="sections-container">
        <section class="slideshow">
          <article class="article--centered">
            <h2>
              Un accompagnement à chaque étape
            </h2>
            <p>
              Docurba centralise les ressources nécessaires à chaque étape de vos procédures d'urbanisme
              pour plus de rapidité, une meilleure conformité, et une visibilité en temps réel.
            </p>
          </article>

          <div class="slideshow__slides-container">
            <LandingSlidingTabs v-model="tab" :options="tabs" />
            <div class="slideshow__slides-container__slide">
              <img :src="`/images/landing/slideshow/${tab}.svg`">
            </div>
          </div>
        </section>

        <section class="collectivites">
          <article>
            <h2>
              Collectivités
            </h2>
            <p>Soyez certain de ne plus rater d'étape et retrouvez facilement toutes les informations utiles à l'élaboration de vos documents d'urbanisme.</p>
          </article>
          <img class="collectivites__image" src="/images/landing/collectivites.png">
        </section>

        <section class="etat">
          <img class="etat__image" src="/images/landing/pac.png">
          <article>
            <h2>
              Services de l'État
            </h2>
            <p>Créez vos Porter à Connaissance plus rapidement grâce à une centralisation et mise à jour constante des éléments nationaux et régionaux, et profitez d'une visibilité en temps réel sur l'avancement des procédures d'urbanisme de vos collectivités.</p>
          </article>
        </section>

        <div class="sections-duo">
          <section class="neutral">
            <article>
              <h2>
                Bureaux d'études
              </h2>
              <p>Accédez à toutes les données de vos territoires en quelques clics et offrez des procédures structurées pour guider vos collectivités. </p>
            </article>
          </section>
          <section class="neutral">
            <article>
              <h2>
                Citoyens
              </h2>
              <p>Suivez l'avancement des projets d'urbanisme de votre collectivité et accédez à toutes les ressources utiles pour mieux comprendre les décisions de vos élus.</p>
            </article>
          </section>
        </div>

        <section class="signup neutral">
          <article class="article--centered">
            <h2>
              Inscrivez-vous pour débuter
            </h2>
            <p>
              Créez votre compte sur Docurba pour éditer vos procédures ou Porter à Connaissance et accélérer vos projets d'urbanisme dès maintenant.
            </p>
          </article>
          <v-btn color="primary" depressed>
            S'inscrire
          </v-btn>
        </section>
      </div>
    </main>
  </div>
</template>

<script>
export default {
  name: 'Landing',
  data () {
    return {
      tab: 'procedures',
      tabs: [
        { label: 'Démarrez vos procédures', value: 'procedures' },
        { label: 'Accédez aux ressources', value: 'resources' },
        { label: 'Documentez les avancées', value: 'frp' }
      ]
    }
  }
}
</script>

<style scoped>
h1 {
  font-size: 3.5rem;
  font-weight: 700;
  line-height: 64px;
}

h2 {
  font-size: 2rem;
  font-weight: 700;
}

section > article {
  display: flex;
  flex-direction: column;
  gap: 1rem;
}

.article--centered {
  align-items: center;
  text-align: center;
}

.article--centered > p {
  max-width: 760px;
}

.landing-container {
  display: flex;
  justify-content: center;
  padding: 4rem 1rem;
}

.landing {
  max-width: 1160px;
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 232px;
}

.hero-section {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 3.5rem;
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

.sections-container {
  display: flex;
  flex-direction: column;
  gap: 4rem;
}

section.slideshow {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 2rem;
}

.slideshow__slides-container {
  display: flex;
  flex-direction: column;
  align-items: center;
}

.slideshow__slides-container__slide {
  padding-top: 5rem;
  padding-bottom: 2rem;
  margin-top: -2.5rem;
  border: 1px solid #DDDDDD;
  border-radius: 0.5rem;
  background-color: #F9F8F6;
  overflow: hidden;
}

.slideshow__slides-container__slide > img {
  width: 100%;
}

section.collectivites {
  display: flex;
  align-items: center;
  gap: 3.5rem;
  padding: 4rem 3rem;
  border-radius: 0.5rem;
  border: 1px solid #E3CF50;
  background-color: #FCE552;
}

.collectivites__image {
  width: 100%;
  max-width: 696px;
  flex-shrink: 0;
  margin-right: -5.5rem;
  border-radius: 0.5rem;
  border: 1px solid #DDDDDD;
  filter: drop-shadow(6px 0px 8px rgba(0, 0, 0, 0.10)) drop-shadow(0px 4px 24px rgba(0, 0, 0, 0.12));
}

section.etat {
  display: flex;
  align-items: center;
  gap: 3.5rem;
  border: 1px solid #B6CFFB;
  border-radius: 0.5rem;
  background-color: #E6EEFE;
  padding: 0 3rem;
}

.etat__image {
  width: 100%;
  max-width: 584px;
  flex-shrink: 0;
  margin-top: -2rem;
  border-top-left-radius: 0.5rem;
  border-top-right-radius: 0.5rem;
  border-top-width: 1px;
  border-left-width: 1px;
  border-right-width: 1px;
  border-color: #DDDDDD;
  filter: drop-shadow(6px 0px 8px rgba(0, 0, 0, 0.10)) drop-shadow(0px 4px 24px rgba(0, 0, 0, 0.12));
}

.sections-duo {
  display: flex;
  gap: 2rem;
}

.sections-duo section {
  flex: 1;
}

section.neutral {
  border: 1px solid #DDDDDD;
  border-radius: 0.5rem;
  background-color: #F9F8F6;
  padding: 3rem 4rem;
}

section.signup {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 2rem;
}

@media screen and (max-width: 960px) {
  h1 {
    font-size: 2.5rem;
    line-height: 48px;
  }

  h2 {
    font-size: 1.5rem;
  }

  .sections-container {
    gap: 2.5rem;
  }

  .slideshow__slides-container__slide {
    padding-top: 8rem;
    margin-top: -6.5rem;
  }

  article {
    align-items: center;
    text-align: center;
  }

  section.collectivites {
    flex-direction: column;
    gap: 2rem;
    padding: 2rem;
  }

  .collectivites__image {
    margin: 0;
  }

  section.etat {
    flex-direction: column-reverse;
    gap: 2rem;
    padding: 2rem;
  }

  .etat__image {
    margin-top: 0;
  }

  .sections-duo {
    flex-direction: column;
  }

  section.neutral {
    padding: 2rem;
  }
}
</style>
