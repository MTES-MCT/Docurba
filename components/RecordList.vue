<template>
  <v-container>
    <v-row>
      <v-col cols="12">
        <v-chip-group
          v-model="selectedCategory"
          column
        >
          <v-chip
            v-for="category in categories"
            :key="category"
            class="text-capitalize"
            :value="category"
            filter
            outlined
            color="bf500"
          >
            {{ category }}
          </v-chip>
        </v-chip-group>
      </v-col>
    </v-row>

    <VGlobalLoader v-if="loading" />
    <v-row v-else>
      <v-col v-for="record in records" :key="record.id" cols="12" sm="6" md="4">
        <RecordCard :record="record" style="height: 100%;" />
      </v-col>
    </v-row>
  </v-container>
</template>

<script>
import axios from 'axios'

export default {
  props: {
    collectiviteCode: {
      type: String,
      required: true
    },
    isEpci: {
      type: Boolean,
      required: true
    }
  },
  data () {
    return {
      records: [],
      categories: [],
      selectedCategory: null,
      loading: false,
      cancelTokenSource: null
    }
  },
  watch: {
    async selectedCategory (newValue) {
      if (newValue == null) {
        this.records = []
        this.loading = false
        return
      }

      this.loading = true

      if (this.cancelTokenSource) {
        this.cancelTokenSource.cancel()
      }

      this.cancelTokenSource = axios.CancelToken.source()

      try {
        const { data } = await axios.get(`/api/data/${this.collectiviteCode}`, {
          params: {
            category: newValue,
            isEpci: this.isEpci
          },
          cancelToken: this.cancelTokenSource.token
        })
        this.cancelTokenSource = null
        this.records = data
        this.loading = false
      } catch (error) {
        if (!axios.isCancel(error)) {
          this.loading = false
          throw error
        }
      }
    }
  },
  async mounted () {
    const { data } = await axios.get(`/api/data/${this.collectiviteCode}/categories`, {
      params: {
        isEpci: this.isEpci
      }
    })
    this.categories = data
  }
}
</script>
