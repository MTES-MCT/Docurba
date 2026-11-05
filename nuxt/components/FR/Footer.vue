<template>
  <footer class="fr-footer">
    <div v-if="$slots.top"
         class="fr-footer__top">
      <FRContainer>
        <slot name="top" />
      </FRContainer>
    </div>
    <div class="fr-footer__banner">
      <FRContainer>
        <slot name="banner" />
      </FRContainer>
    </div>
    <div class="fr-footer__body">
      <FRContainer>
        <div class="fr-footer__row">
          <FRActionable class="fr-footer__brand"
                        to="/dsfr">
            <slot name="brand" />
          </FRActionable>
          <div class="fr-footer__description">
            <slot name="description" />
          </div>
        </div>
        <ul class="fr-footer__links">
          <slot name="links" />
        </ul>
        <FRText mention
                xs>
          <slot name="mention" />
        </FRText>
      </FRContainer>
    </div>
  </footer>
</template>

<style>
.fr-footer {
  background-color: var(--fr-color__grey-1000-50);
  box-shadow: inset 0 .125rem 0 0 var(--fr-color__blue-france-sun-113-625),
              inset 0 -.0625rem 0 0 var(--fr-color__grey-900-175);
  display: grid;
}
.fr-footer__banner {
  background-color: var(--fr-color__blue-france-main-525);
  display: grid;
  padding-bottom: 2rem;
  padding-top: 2rem;
}
.fr-footer__banner:first-child {
  margin-top: .125rem;
  padding-top: 1.875rem;
}
.fr-footer__banner > .fr-container {
  column-gap: 5rem;
  grid-auto-flow: column;
  justify-content: start;
}
.fr-footer__banner a,
.fr-footer__banner [tabindex] {
  align-items: center;
  color: var(--fr-color__grey-1000-50);
  column-gap: .25rem;
  display: grid;
  font-size: .75rem;
  grid-auto-flow: column;
  line-height: 1.25rem;
  text-decoration: none;
}
.fr-footer__banner a:focus-visible,
.fr-footer__banner a:hover,
.fr-footer__banner [tabindex]:focus-visible
.fr-footer__banner [tabindex]:hover {
  box-shadow: inset 0 -.0625rem 0 0 currentColor;
}
.fr-footer__banner .fr-icon {
  --fr-icon__size: 1rem;
}
.fr-footer__body {
  display: grid;
  padding-bottom: 1rem;
  padding-top: 2rem;
}
.fr-footer__brand {
  align-self: start;
  color: var(--fr-color__grey-0-1000);
  font-size: 1.3125rem;
  font-weight: 700;
  justify-self: start;
  letter-spacing: -.01em;
  line-height: 1.0317460317em;
  margin-bottom: -1rem;
  margin-left: -1rem;
  margin-top: -1rem;
  padding: 1rem;
  text-decoration: none;
  text-indent: -.1em;
  text-transform: uppercase;
}
.fr-footer__brand:focus-visible,
.fr-footer__brand:hover {
  background-color: var(--fr-color__grey-1000-50--hover);
}
.fr-footer__brand::before {
  background-image: url('~/assets/images/marianne.svg'),
                    linear-gradient(90deg, #000091, #000091, 50%, #e1000f 0, #e1000f),
                    linear-gradient(90deg, #000, #000);
  background-position: 0 -.078125rem,
                       0 0,
                       0 0;
  background-size: 3.4375rem 1.40625rem,
                   3.4375rem 1.25rem,
                   0;
  content: '';
  display: block;
  height: 1.25rem;
  margin-bottom: .4166666667rem;
  width: 3.4375rem;
}
.fr-footer__brand::after {
  background-image: url('~/assets/images/liberte-egalite-fraternite.svg');
  background-position: 0 calc(100% + 2.34375rem);
  background-repeat: no-repeat;
  background-size: 6.5625rem 4.6875rem;
  content: '';
  display: block;
  height: 2.7604166667rem;
  width: 3.28125rem;
}
.fr-footer__description {
  align-content: start;
  display: grid;
  row-gap: 1.5rem;
}
.fr-footer__links {
  align-items: center;
  box-shadow: inset 0 .0625rem 0 0 var(--fr-color__grey-900-175);
  column-gap: 1rem;
  display: grid;
  grid-auto-flow: column;
  justify-content: start;
  list-style: none;
  margin-top: 1.5rem;
  padding-bottom: 1rem;
  padding-top: .5rem;
}
.fr-footer__links > li {
  align-items: center;
  column-gap: 1rem;
  display: grid;
  grid-auto-flow: column;
}
.fr-footer__links > li:not(:first-child)::before {
  background-color: var(--fr-color__grey-900-175);
  content: '';
  height: 1rem;
  width: .0625rem;
}
.fr-footer__links > li > a,
.fr-footer__links > li > [tabindex] {
  color: var(--fr-color__grey-425-625);
  cursor: pointer;
  font-size: .75rem;
  line-height: 1.25rem;
  text-decoration: none;
}
.fr-footer__links > li > a:focus-visible,
.fr-footer__links > li > a:hover,
.fr-footer__links > li > [tabindex]:focus-visible,
.fr-footer__links > li > [tabindex]:hover {
  box-shadow: inset 0 -.0625rem 0 0 currentColor;
}
.fr-footer__row {
  display: grid;
  grid-auto-columns: 1fr;
  grid-auto-flow: column;
}
.fr-footer__top {
  background-color: var(--fr-color__blue-france-975-75);
  display: grid;
  margin-top: .125rem;
  padding-bottom: 2rem;
  padding-top: 1.875rem;
}

[data-fr-theme="dark"] .fr-footer__brand::after {
  background-position: -3.28125rem 100%;
}
</style>
