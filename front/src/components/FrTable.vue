<template>
  <div class="fr-table__wrapper">
    <div class="fr-table__container">
      <table class="fr-table">
        <thead>
          <tr>
            <slot name="header" />
          </tr>
        </thead>
        <tbody>
          <slot />
        </tbody>
      </table>
    </div>
  </div>
</template>

<style>
.fr-table {
  border-collapse: collapse;
  border-spacing: 0;
  width: 100%;
}
.fr-table td,
.fr-table th {
  color: var(--color-grey-200-850);
  font-family: var(--font-family-sans);
  font-size: .875rem;
  line-height: 1.5rem;
  padding: .5rem 1rem;
  vertical-align: middle;
}
.fr-table td {
  font-weight: 400;
}
.fr-table th {
  background-color: var(--color-grey-975-75);
  box-shadow: inset 0 -.0625rem 0 0 var(--color-grey-200-850),
              inset -.0625rem 0 0 0 var(--color-grey-900-175);
  font-weight: 700;
  text-align: left;
}
.fr-table th:empty {
  width: 0;
}
.fr-table tr:focus-within,
.fr-table tr:hover {
  background-color: var(--color-grey-1000-50-hover);
}
.fr-table__container {
  display: grid;
  max-width: 100%;
  overflow: auto;
}
.fr-table__wrapper {
  background-color: var(--color-grey-1000-50);
  display: grid;
  position: relative;
}
.fr-table__wrapper::after {
  box-shadow: inset 0 0 0 .0625rem var(--color-grey-425-625);
  content: '';
  inset: 0;
  pointer-events: none;
  position: absolute;
}
</style>
