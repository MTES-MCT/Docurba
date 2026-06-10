<script setup lang="ts">
import FrButton from '@/components/FrButton.vue'
</script>

<template>
  <header class="fr-header"
          id="header"
          role="banner">
    <div class="fr-header__body">
      <div class="fr-container">
        <div class="fr-header__body-row">
          <div class="fr-header__brand fr-enlarge-link">
            <div class="fr-header__brand-top">
              <div class="fr-header__logo">
                <p class="fr-logo">
                  République<br>
                  Française
                </p>
              </div>
              <div class="fr-header__navbar">
                <FrButton aria-controls="header-menu"
                          data-fr-opened="false"
                          id="header-menu-btn"
                          menu
                          title="Menu">Menu</FrButton>
              </div>
            </div>
            <div class="fr-header__service">
              <RouterLink title="Retour à l'accueil du site - Docurba - République Française"
                          to="/">
                <p class="fr-header__service-title">Docurba</p>
              </RouterLink>
            </div>
          </div>
          <div class="fr-header__tools">
            <div class="fr-header__tools-links">
              <ul class="fr-btns-group">
                <li>
                  <FrButton sm
                            to="/tableau-de-bord">Tableau de bord</FrButton>
                </li>
                <li>
                  <FrButton sm
                            to="/documentation">Documentation</FrButton>
                </li>
                <li>
                  <FrButton icon="arrow-down-s-line"
                            icon-right
                            sm>Etienne</FrButton>
                </li>
              </ul>
            </div>
          </div>
        </div>
      </div>
    </div>
    <div aria-labelledby="header-menu-btn"
         class="fr-header__menu fr-modal"
         id="header-menu">
      <div class="fr-container">
        <FrButton aria-controls="header-menu"
                  close
                  title="Fermer" type="button">Fermer</FrButton>
        <div class="fr-header__menu-links">
          <ul class="fr-btns-group">
            <li>
              <FrButton sm
                        to="/tableau-de-bord">Tableau de bord</FrButton>
            </li>
            <li>
              <FrButton sm>Documentation</FrButton>
            </li>
            <li>
              <FrButton icon="arrow-down-s-line"
                        icon-right
                        sm>Etienne</FrButton>
            </li>
          </ul>
        </div>
      </div>
    </div>
  </header>
<RouterView />
</template>
