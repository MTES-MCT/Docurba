<script>
export default {
  props: {
    actionableChild: {
      default: false,
      type: Boolean,
    },
    disabled: {
      default: false,
      type: Boolean,
    },
    to: {
      default: undefined,
      type: [String, Object],
    },
    // Sizes
    sm: {
      default: false,
      type: Boolean,
    },
    // Variations
    beigeGrisGalet: {
      default: false,
      type: Boolean,
    },
    blueCumulus: {
      default: false,
      type: Boolean,
    },
    blueEcume: {
      default: false,
      type: Boolean,
    },
    brownCafeCreme: {
      default: false,
      type: Boolean,
    },
    brownCaramel: {
      default: false,
      type: Boolean,
    },
    brownOpera: {
      default: false,
      type: Boolean,
    },
    greenArchipel: {
      default: false,
      type: Boolean,
    },
    greenBourgeon: {
      default: false,
      type: Boolean,
    },
    greenEmeraude: {
      default: false,
      type: Boolean,
    },
    greenMenthe: {
      default: false,
      type: Boolean,
    },
    greenTilleulVerveine: {
      default: false,
      type: Boolean,
    },
    orangeTerreBattue: {
      default: false,
      type: Boolean,
    },
    pinkMacaron: {
      default: false,
      type: Boolean,
    },
    pinkTuile: {
      default: false,
      type: Boolean,
    },
    purpleGlycine: {
      default: false,
      type: Boolean,
    },
    yellowMoutarde: {
      default: false,
      type: Boolean,
    },
    yellowTournesol: {
      default: false,
      type: Boolean,
    },
  },
  computed: {
    actionable() {
      return !!this.to || !!this.$listeners.actuated
    },
  },
}
</script>

<template>
  <component :is="actionable ? 'FRActionable' : 'div'"
             class="fr-tag"
             :class="{
               'fr-tag--actionable-child': actionableChild,
               'fr-tag--beige-gris-galet': beigeGrisGalet,
               'fr-tag--blue-cumulus': blueCumulus,
               'fr-tag--blue-ecume': blueEcume,
               'fr-tag--brown-cafe-creme': brownCafeCreme,
               'fr-tag--brown-caramel': brownCaramel,
               'fr-tag--brown-opera': brownOpera,
               'fr-tag--green-archipel': greenArchipel,
               'fr-tag--green-bourgeon': greenBourgeon,
               'fr-tag--green-emeraude': greenEmeraude,
               'fr-tag--green-menthe': greenMenthe,
               'fr-tag--green-tilleul-verveine': greenTilleulVerveine,
               'fr-tag--orange-terre-battue': orangeTerreBattue,
               'fr-tag--pink-macaron': pinkMacaron,
               'fr-tag--pink-tuile': pinkTuile,
               'fr-tag--purple-glycine': purpleGlycine,
               'fr-tag--sm': sm,
               'fr-tag--yellow-moutarde': yellowMoutarde,
               'fr-tag--yellow-tournesol': yellowTournesol,
             }"
             :disabled="actionable ? disabled : undefined"
             :to="to"
             @actuated="$emit('actuated', $event)">
    <slot />
  </component>
</template>

<style>
.fr-tag {
  --fr-tag__bg: var(--fr-color__grey-950-100);
  --fr-tag__bg-active: var(--fr-color__grey-950-100);
  --fr-tag__color: var(--fr-color__grey-50-1000);

  align-items: center;
  background-color: var(--fr-tag__bg);
  border-radius: 1rem;
  color: var(--fr-tag__color);
  column-gap: .5rem;
  display: grid;
  font-size: .875rem;
  font-weight: 400;
  grid-auto-flow: column;
  line-height: 1.5rem;
  padding: .25rem .75rem;
}
.fr-tag:focus-visible,
.fr-tag:hover {
  background-color: var(--fr-tag__bg-active);
}
.fr-tag > .fr-icon {
  --fr-icon__size: 1rem;

  margin: .25rem -.25rem;
}
.fr-tag[disabled] {
  --fr-tag__bg: var(--fr-color__grey-925-125);
  --fr-tag__bg-active: var(--fr-color__grey-925-125);
  --fr-tag__color: var(--fr-color__grey-625-425);

  cursor: not-allowed;
}
a.fr-tag,
.fr-tag[tabindex],
.fr-tag--actionable-child {
  --fr-tag__bg: var(--fr-color__blue-france-925-125);
  --fr-tag__color: var(--fr-color__blue-france-sun-113-625);
}
a.fr-tag,
.fr-tag[tabindex] {
  --fr-tag__bg-active: var(--fr-color__blue-france-925-125--hover);

  cursor: pointer;
  text-decoration: none;
}
.fr-tag--actionable-child {
  --fr-tag__bg-active: var(--fr-color__blue-france-925-125);
}
/* Sizes */
.fr-tag--sm {
  border-radius: .75rem;
  column-gap: .375rem;
  font-size: .75rem;
  line-height: 1.25rem;
  padding: .125rem .5rem;
}
.fr-tag--sm > .fr-icon {
  --fr-icon__size: .75rem;

  margin-left: -.125rem;
  margin-right: -.125rem;
}
/* Variations */
a.fr-tag--beige-gris-galet,
.fr-tag--beige-gris-galet[tabindex] {
  --fr-tag__bg: var(--fr-color__beige-gris-galet-925-125);
  --fr-tag__bg-active: var(--fr-color__beige-gris-galet-925-125--hover);
  --fr-tag__color: var(--fr-color__beige-gris-galet-sun-407-moon-821);
}
a.fr-tag--blue-cumulus,
.fr-tag--blue-cumulus[tabindex] {
  --fr-tag__bg: var(--fr-color__blue-cumulus-925-125);
  --fr-tag__bg-active: var(--fr-color__blue-cumulus-925-125--hover);
  --fr-tag__color: var(--fr-color__blue-cumulus-sun-368-moon-732);
}
a.fr-tag--blue-ecume,
.fr-tag--blue-ecume[tabindex] {
  --fr-tag__bg: var(--fr-color__blue-ecume-925-125);
  --fr-tag__bg-active: var(--fr-color__blue-ecume-925-125--hover);
  --fr-tag__color: var(--fr-color__blue-ecume-sun-247-moon-675);
}
a.fr-tag--brown-cafe-creme,
.fr-tag--brown-cafe-creme[tabindex] {
  --fr-tag__bg: var(--fr-color__brown-cafe-creme-925-125);
  --fr-tag__bg-active: var(--fr-color__brown-cafe-creme-925-125--hover);
  --fr-tag__color: var(--fr-color__brown-cafe-creme-sun-383-moon-885);
}
a.fr-tag--brown-caramel,
.fr-tag--brown-caramel[tabindex] {
  --fr-tag__bg: var(--fr-color__brown-caramel-925-125);
  --fr-tag__bg-active: var(--fr-color__brown-caramel-925-125--hover);
  --fr-tag__color: var(--fr-color__brown-caramel-sun-425-moon-901);
}
a.fr-tag--brown-opera,
.fr-tag--brown-opera[tabindex] {
  --fr-tag__bg: var(--fr-color__brown-opera-925-125);
  --fr-tag__bg-active: var(--fr-color__brown-opera-925-125--hover);
  --fr-tag__color: var(--fr-color__brown-opera-sun-395-moon-820);
}
a.fr-tag--green-archipel,
.fr-tag--green-archipel[tabindex] {
  --fr-tag__bg: var(--fr-color__green-archipel-925-125);
  --fr-tag__bg-active: var(--fr-color__green-archipel-925-125--hover);
  --fr-tag__color: var(--fr-color__green-archipel-sun-391-moon-716);
}
a.fr-tag--green-bourgeon,
.fr-tag--green-bourgeon[tabindex] {
  --fr-tag__bg: var(--fr-color__green-bourgeon-925-125);
  --fr-tag__bg-active: var(--fr-color__green-bourgeon-925-125--hover);
  --fr-tag__color: var(--fr-color__green-bourgeon-sun-425-moon-759);
}
a.fr-tag--green-emeraude,
.fr-tag--green-emeraude[tabindex] {
  --fr-tag__bg: var(--fr-color__green-emeraude-925-125);
  --fr-tag__bg-active: var(--fr-color__green-emeraude-925-125--hover);
  --fr-tag__color: var(--fr-color__green-emeraude-sun-425-moon-753);
}
a.fr-tag--green-menthe,
.fr-tag--green-menthe[tabindex] {
  --fr-tag__bg: var(--fr-color__green-menthe-925-125);
  --fr-tag__bg-active: var(--fr-color__green-menthe-925-125--hover);
  --fr-tag__color: var(--fr-color__green-menthe-sun-373-moon-652);
}
a.fr-tag--green-tilleul-verveine,
.fr-tag--green-tilleul-verveine[tabindex] {
  --fr-tag__bg: var(--fr-color__green-tilleul-verveine-925-125);
  --fr-tag__bg-active: var(--fr-color__green-tilleul-verveine-925-125--hover);
  --fr-tag__color: var(--fr-color__green-tilleul-verveine-sun-418-moon-817);
}
a.fr-tag--orange-terre-battue,
.fr-tag--orange-terre-battue[tabindex] {
  --fr-tag__bg: var(--fr-color__orange-terre-battue-925-125);
  --fr-tag__bg-active: var(--fr-color__orange-terre-battue-925-125--hover);
  --fr-tag__color: var(--fr-color__orange-terre-battue-sun-370-moon-672);
}
a.fr-tag--pink-macaron,
.fr-tag--pink-macaron[tabindex] {
  --fr-tag__bg: var(--fr-color__pink-macaron-925-125);
  --fr-tag__bg-active: var(--fr-color__pink-macaron-925-125--hover);
  --fr-tag__color: var(--fr-color__pink-macaron-sun-406-moon-833);
}
a.fr-tag--pink-tuile,
.fr-tag--pink-tuile[tabindex] {
  --fr-tag__bg: var(--fr-color__pink-tuile-925-125);
  --fr-tag__bg-active: var(--fr-color__pink-tuile-925-125--hover);
  --fr-tag__color: var(--fr-color__pink-tuile-sun-425-moon-750);
}
a.fr-tag--purple-glycine,
.fr-tag--purple-glycine[tabindex] {
  --fr-tag__bg: var(--fr-color__purple-glycine-925-125);
  --fr-tag__bg-active: var(--fr-color__purple-glycine-925-125--hover);
  --fr-tag__color: var(--fr-color__purple-glycine-sun-319-moon-630);
}
a.fr-tag--yellow-moutarde,
.fr-tag--yellow-moutarde[tabindex] {
  --fr-tag__bg: var(--fr-color__yellow-moutarde-925-125);
  --fr-tag__bg-active: var(--fr-color__yellow-moutarde-925-125--hover);
  --fr-tag__color: var(--fr-color__yellow-moutarde-sun-348-moon-860);
}
a.fr-tag--yellow-tournesol,
.fr-tag--yellow-tournesol[tabindex] {
  --fr-tag__bg: var(--fr-color__yellow-tournesol-925-125);
  --fr-tag__bg-active: var(--fr-color__yellow-tournesol-925-125--hover);
  --fr-tag__color: var(--fr-color__yellow-tournesol-sun-407-moon-922);
}
</style>
