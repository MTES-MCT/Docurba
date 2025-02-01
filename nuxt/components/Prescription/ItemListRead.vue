<template>
  <div>
    <div v-if="value && value.type === 'link'">
      <v-row
        align="center"
      >
        <v-col cols="8" class="d-flex">
          <div>
            Lien vers le <a target="__blank" :href="value.link_url">Document de prescription</a>
          </div>
          <div>
            &nbsp;déposé le {{ $dayjs(value.created_at).format('DD/MM/YYYY') }}
          </div>
        </v-col>
        <v-col cols="4">
          <v-btn
            class="pa-0"
            outlined
            color="primary"
            @click="copyLinktoClip"
          >
            <v-icon>{{ icons.mdiLink }}</v-icon>
          </v-btn>
          <v-btn
            class="pa-0"
            outlined
            color="primary"
            target="__blank"
            :href="value.link_url"
          >
            <v-icon>{{ icons.mdiEye }}</v-icon>
          </v-btn>
        </v-col>
      </v-row>
    </div>

    <div v-if="value && value.type === 'attachments'">
      <v-row
        v-for="prescrData in value.attachments"
        :key="`prescrData-${prescrData.id}`"
        align="center"
      >
        <v-col cols="8" class="d-flex">
          <div>
            Fichier <a target="__blank" href="" @click="downloadFile(prescrData)">{{ prescrData.name }}</a>
          </div>
          <a :ref="`file-${prescrData.id}`" :download="prescrData.name" class="d-none" />
          <div>
            &nbsp;déposé le {{ $dayjs(value.created_at).format('DD/MM/YYYY') }}
          </div>
        </v-col>
        <v-col cols="4">
          <v-btn
            class="pa-0"
            outlined
            color="primary"
            @click="getFileLink(prescrData)"
          >
            <v-icon>{{ icons.mdiLink }}</v-icon>
          </v-btn>
          <v-btn
            class="pa-0"
            outlined
            color="primary"
            @click="downloadFile(prescrData)"
          >
            <v-icon>{{ icons.mdiDownload }}</v-icon>
          </v-btn>
        </v-col>
      </v-row>
    </div>
  </div>
</template>

<script>
import { mdiDownload, mdiEye, mdiLink } from '@mdi/js'

export default {
  name: 'ItemListReadPrescription',
  props: {
    value: {
      type: Object,
      required: true
    }
  },
  data () {
    return {
      icons: {
        mdiDownload,
        mdiEye,
        mdiLink
      }
    }
  },
  methods: {
    getFileLink (file) {
      console.log('file:', file)
      const { data } = this.$supabase
        .storage
        .from('prescriptions')
        .getPublicUrl(file.path)
      console.log('data: ', data)
      navigator.clipboard.writeText(data.publicUrl)
      // this.snackClip = true
      this.$emit('snack', true)
      return data.publicUrl
    },
    async downloadFile (file) {
      const { data } = await this.$supabase.storage.from('prescriptions').download(file.path)
      const link = this.$refs[`file-${file.id}`][0]
      link.href = URL.createObjectURL(data)
      link.click()
    },
    copyLinktoClip () {
      navigator.clipboard.writeText(this.value.link_url)
      // this.snackClip = true
      this.$emit('snack', true)
    }
  }
}
</script>
