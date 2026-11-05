<template>
  <header class="fr-header">
    <FRContainer>
      <div class="fr-header__body">
        <FRActionable class="fr-header__brand"
                      to="/dsfr">
          <div class="fr-header__logo">
            <slot name="brand" />
          </div>
          <FRText h6>
            <slot name="heading" />
          </FRText>
        </FRActionable>
        <div class="fr-header__links">
          <slot name="links" />
        </div>
      </div>
    </FRContainer>
    <slot />
  </header>
</template>

<style>
.fr-header {
  align-items: center;
  background-color: var(--fr-color__grey-1000-50);
  box-shadow: var(--fr-shadow__raised);
  display: grid;
  position: sticky;
  top: 0;
  z-index: var(--fr-index__header);
}
.fr-header__body {
  align-items: center;
  display: grid;
  grid-auto-flow: column;
  justify-content: space-between;
  padding-bottom: 1rem;
  padding-top: 1rem;
}
.fr-header__brand {
  align-items: center;
  column-gap: 2rem;
  cursor: pointer;
  display: grid;
  grid-auto-flow: column;
  margin-bottom: -1rem;
  margin-left: -1rem;
  margin-top: -1rem;
  padding: 1rem;
  text-decoration: none;
}
.fr-header__brand:focus-visible,
.fr-header__brand:hover {
  background-color: var(--fr-color__grey-1000-50--hover);
}
.fr-header__links {
  align-items: center;
  column-gap: .5rem;
  display: grid;
  grid-auto-flow: column;
}
.fr-header__logo {
  color: var(--fr-color__grey-0-1000);
  font-size: .7875rem;
  font-weight: 700;
  letter-spacing: -.01em;
  line-height: 1.0317460317em;
  text-indent: -.1em;
  text-transform: uppercase;
}
.fr-header__logo::before {
  background-image: url('~/assets/images/marianne.svg'),
                    linear-gradient(90deg, #000091, #000091, 50%, #e1000f 0, #e1000f),
                    linear-gradient(90deg, #000, #000);
  background-position: 0 -.046875rem,
                       0 0,
                       0 0;
  background-size: 2.0625rem .84375rem,
                   2.0625rem .75rem,
                   0;
  content: '';
  display: block;
  height: .75rem;
  margin-bottom: .25rem;
  width: 2.0625rem;
}
.fr-header__logo::after {
  background-image: url('~/assets/images/liberte-egalite-fraternite.svg');
  background-position: 0 calc(100% + 1.40625rem);
  background-repeat: no-repeat;
  background-size: 3.9375rem 2.8125rem;
  content: '';
  display: block;
  height: 1.65625rem;
  width: 1.96875rem;
}

@media (min-width: 62rem) {
  .fr-header__body {
    padding-bottom: 1.5rem;
    padding-top: 1.5rem;
  }
}

[data-fr-theme="dark"] .fr-header__logo::after {
  background-position: -1.96875rem 100%;
}
</style>
