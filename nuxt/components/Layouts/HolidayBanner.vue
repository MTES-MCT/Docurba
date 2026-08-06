<template>
  <div>
    <div
      v-if="visible"
      role="status"
      class="align-center bf200 d-flex justify-center primary--text px-4 py-3 text--lighten-2 text-body-2"
    >
      <v-icon class="mr-2" style="color: inherit" size="20">
        {{ icons.mdiInformation }}
      </v-icon>
      <span>
        Nous travaillons en équipe réduite jusqu'au {{ displayedToDate }}, nos délais de réponses pourraient donc être rallongés, merci de votre compréhension.<br>
        Pensez à consulter notre <a href="https://docurba.crisp.help/fr/" target="_blank">Centre d'Aide</a>.
      </span>
    </div>
  </div>
</template>

<script>
import { mdiInformation } from '@mdi/js'

const HOLIDAY_FROM = '2026-08-07'
const HOLIDAY_TO = '2026-08-28'

export default {
  name: 'HolidayBanner',
  data () {
    return {
      icons: {
        mdiInformation
      }
    }
  },
  computed: {
    displayedToDate () {
      return this.toDate.format('D MMMM')
    },
    fromDate () {
      return this.$dayjs(HOLIDAY_FROM)
    },
    toDate () {
      return this.$dayjs(HOLIDAY_TO)
    },
    visible () {
      return !!this.$user && this.visibleOnDate && this.visibleOnPage
    },
    visibleOnDate () {
      const now = new Date()

      return now >= this.fromDate && now < this.toDate.add(1, 'day')
    },
    visibleOnPage () {
      return [
        'collectivites-collectiviteId',
        'ddt-departement-collectivites',
        'ddt-departement-pac'
      ].includes(this.$route.name)
    }
  }
}
</script>
