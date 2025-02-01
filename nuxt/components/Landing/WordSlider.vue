<template>
  <div class="slider-container">
    <div class="slider">
      <h1>PLU</h1>
      <h1>PLUi</h1>
      <h1>SCoT</h1>
      <h1>PLU</h1>
    </div>
  </div>
</template>

<style scoped>
@keyframes slider {
  0%, 27% {
      transform: translateY(0%);
  }
  33%, 60% {
      transform: translateY(-25%);
  }
  66%, 93% {
      transform: translateY(-50%);
  }
  100% {
      transform: translateY(-75%);
  }
}

.slider-container {
  display: inline-block;
  vertical-align: bottom;
  background-color: #FCE552;
  height: 3.5rem;
  padding: 0 0.5rem;
  text-align: center;
  overflow: hidden;
}

.slider {
  margin-top: -5px; /* fix the small offset above texts */
  animation: slider ease-in-out 7s infinite;
}

.slider h1 {
  font-size: 3.5rem;
  height: 3.5rem;
  line-height: 3.5rem;
  font-weight: 700;
}

@media screen and (max-width: 960px) {
  .slider-container {
    height: 2.5rem;
  }

  .slider h1 {
    font-size: 2.5rem;
    height: 2.5rem;
    line-height: 2.5rem;
  }
}
</style>
