<template>
  <v-card color="beige" flat class="position-relative">
    <VFloatingShape src="/images/landing/ellipse_blue.svg" :size="72" :right="15" :top="-50" />
    <v-card-title>
      <b>Consultez les socles de PAC déjà disponibles</b>
    </v-card-title>
    <v-card-text>
      <v-row>
        <v-col v-for="(regionsList, i) in regionsLists" :key="i" cols="4">
          <v-list color="beige">
            <template v-for="region in regionsList">
              <v-list-item :key="region.iso + '-item'">
                <v-list-item-content>
                  <v-list-item-title>
                    {{ region.name }}
                  </v-list-item-title>
                </v-list-item-content>
                <v-list-item-action>
                  <v-icon color="primary">
                    {{ icons.mdiChevronRight }}
                  </v-icon>
                </v-list-item-action>
              </v-list-item>
              <v-divider :key="region.iso + '-divider'" />
            </template>
          </v-list>
        </v-col>
      </v-row>
    </v-card-text>
  </v-card>
</template>

<script>
import { mdiChevronRight } from '@mdi/js'
import regions from '@/assets/data/Regions.json'
export default {
  data () {
    const regionsLists = []
    const chunkSize = 6

    for (let i = 0; i < regions.length; i += chunkSize) {
      regionsLists.push(regions.slice(i, i + chunkSize))
    }

    return {
      regionsLists,
      icons: {
        mdiChevronRight
      }
    }
  }
}
</script>
