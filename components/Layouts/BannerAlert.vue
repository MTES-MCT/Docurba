<template>
  <div>
    <v-alert v-if="currentMessage" type="info">
      {{ currentMessage.preText }}
      <a
        class="white--text"
        :href="currentMessage.url"
        target="_blank"
      >{{ currentMessage.aText }}</a>
      {{ currentMessage.afterText }}
    </v-alert>
  </div>
</template>

<script>
export default {
  data () {
    return {
      messages: [{
        preText: 'Flash Info ce mardi 23 juillet, ',
        aText: 'inscrivez-vous via ce lien.',
        afterText: '',
        url: 'https://app.livestorm.co/mte/flash-info-de-docurba?type=detailed',
        from: this.$dayjs('2024-06-26'),
        to: this.$dayjs('2024-07-23')
      }, {
        preText: "Nous travaillons en équipe réduite jusqu'au 22 août, merci de votre compréhension. Pensez à consulter notre",
        aText: "Centre d'Aide.",
        afterText: '',
        url: 'https://docurba.crisp.help/fr/',
        from: this.$dayjs('2024-07-23'),
        to: this.$dayjs('2024-08-22')
      }]
    }
  },
  computed: {
    currentMessage () {
      return this.messages.find((message) => {
        return message.from.isBefore(this.$dayjs()) && message.to.isAfter(this.$dayjs())
      })
    }
  }
}
</script>
