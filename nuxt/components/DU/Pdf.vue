<template>
  <div class="du-pdf">
    <div class="du-pdf__cover">
      <div class="du-pdf__header">
        <slot name="header" />
      </div>
      <h1>
        <slot name="title" />
      </h1>
    </div>
    <slot />
  </div>
</template>

<style>
.du-pdf {
  box-shadow: 0 0 1rem 0 #000;
  color: #000;
  display: grid;
  font-family: Marianne, Arial, sans-serif;
  font-size: 10pt;
  line-height: 1.5;
  margin-left: auto;
  margin-right: auto;
  overflow-wrap: anywhere;
  padding: 17mm;
  text-align: justify;
  width: 210mm;
}
.du-pdf a {
  color: #000091;
  text-decoration: underline;
}
.du-pdf h1 {
  font-size: 40pt;
  font-weight: 400;
  margin-bottom: 0 !important;
  text-align: center;
}
.du-pdf h2,
.du-pdf h3,
.du-pdf h4,
.du-pdf h5,
.du-pdf h6 {
  margin-bottom: 12pt;
  text-align: left;
}
.du-pdf h2 {
  font-size: 20pt;
  margin-top: 17mm;
}
.du-pdf h3,
.du-pdf h4,
.du-pdf h5,
.du-pdf h6 {
  margin-top: 12pt;
}
.du-pdf h3 {
  font-size: 18pt;
}
.du-pdf h4 {
  font-size: 16pt;
}
.du-pdf h5 {
  font-size: 14pt;
}
.du-pdf h6 {
  font-size: 12pt;
}
.du-pdf img {
  margin-bottom: 10pt;
}
.du-pdf mark {
  background-color: #ffff00;
}
.du-pdf ol,
.du-pdf ul {
  margin-bottom: 10pt;
  padding-left: 12pt;
}
.du-pdf p {
  margin-bottom: 10pt;
}
.du-pdf table {
  margin-bottom: 10pt;
}
.du-pdf th {
  background-color: #f1f3f5;
  font-weight: 700;
}
.du-pdf .column-block {
  column-gap: 12pt;
  display: grid;
  grid-auto-columns: 1fr;
  grid-auto-flow: column;
  margin-bottom: -10pt;
}
.du-pdf__cover {
  align-items: center;
  display: grid;
  grid-auto-rows: auto 1fr;
  justify-items: center;
}
.du-pdf__header {
  align-items: start;
  display: grid;
  grid-auto-flow: column;
  justify-content: space-between;
  justify-self: stretch;
}
.du-pdf__header p:last-child {
  text-align: right;
}

@media print {
  .du-pdf {
    box-shadow: none;
    padding: 0;
    width: auto;
  }
  .du-pdf h2 {
    margin-top: 0;
    page-break-before: always;
  }
  .du-pdf__cover {
    height: 263mm;
  }
}

@page {
  @bottom-right {
    color: #000;
    font-family: Marianne, Arial, sans-serif;
    font-size: 10pt;
    line-height: 1.5;
    content: counter(page);
  }
}
</style>
