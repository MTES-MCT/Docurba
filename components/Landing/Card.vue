<template>
  <section class="landing-card" :class="`card-${color}`">
    <slot>
      <img v-if="imgSide === 'left' && imgSrc" class="hidden-sm-and-down card-img img-left" :src="imgSrc">
      <article>
        <h2 class="card-title">
          {{ title }}
        </h2>
        <p>{{ text }}</p>
      </article>
      <img v-if="imgSrc" class="card-img img-right" :class="imgSide === 'left' ? 'hidden-md-and-up' : ''" :src="imgSrc">
    </slot>
  </section>
</template>

<script>
export default {
  props: {
    imgSrc: {
      type: String,
      default: ''
    },
    imgSide: {
      type: String,
      default: 'right',
      validator (value) { return ['right', 'left'].includes(value) }
    },
    title: {
      type: String,
      default: ''
    },
    text: {
      type: String,
      default: ''
    },
    color: {
      type: String,
      default: 'neutral'
    }
  }
}
</script>

<style scoped>
section > article {
  display: flex;
  flex-direction: column;
  gap: 1rem;
}

@media screen and (max-width: 960px) {
  .landing-card {
    flex-direction: column;
    gap: 2rem;
  }

  article {
    align-items: center;
    text-align: center;
  }

  .card-img.img-right {
    margin-right: 0px !important;
    margin-bottom: 0px !important;
}

.card-img.img-left {
    margin-left: 0px !important;
    margin-bottom: 0px !important;
}
}

.card-title {
  font-size: 2rem;
  font-weight: 700;
}

.landing-card {
  display: flex;
  align-items: center;
  gap: 3.5rem;
  padding: 4rem 3rem;
  border-radius: 0.5rem;
}

.landing-card.card-yellow {
  border: 1px solid #E3CF50;
  background-color: #FCE552;
}

.landing-card.card-blue {
  border: 1px solid #B6CFFB;
  background-color: #E6EEFE;
}

.landing-card.card-neutral {
  border: 1px solid #DDDDDD;
  background-color: #F9F8F6;
}

.card-img {
  height: 100%;
  width: auto;
  max-width: 600px;
  flex-shrink: 0;
  border-radius: 0.5rem;
  border: 1px solid #DDDDDD;
  filter: drop-shadow(6px 0px 8px rgba(0, 0, 0, 0.10)) drop-shadow(0px 4px 24px rgba(0, 0, 0, 0.12));
}

.card-img.img-right {
    margin-right: -48px;
    margin-bottom: -64px;
}

.card-img.img-left {
    margin-left: -48px;
    margin-bottom: -64px;
}
</style>
