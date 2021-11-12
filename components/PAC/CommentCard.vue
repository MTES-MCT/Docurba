<template>
  <v-card>
    <v-card-title>
      {{ section.titre }}
    </v-card-title>
    <v-card-text>
      <v-row class="comments-row">
        <v-col v-for="(comment, i) in section.comments" :key="i" cols="12">
          <v-textarea
            :value="comment.text"
            readonly
            filled
            :label="`${comment.user.firstname} ${comment.user.lastname}`"
            :hint="getCommentDate(comment)"
            persistent-hint
          />
        </v-col>
      </v-row>
    </v-card-text>
    <v-card-actions>
      <v-row>
        <v-col cols="12">
          <v-divider class="mb-2" />
          <v-textarea v-model="newComment.text" filled />
        </v-col>
        <v-col cols="1" />
        <v-spacer />
        <v-col cols="auto" @click="saveNewComment">
          <v-btn>envoyer</v-btn>
        </v-col>
      </v-row>
    </v-card-actions>
  </v-card>
</template>
<script>
import dayjs from 'dayjs'
import pacProject from '@/mixins/pacProject.js'

export default {
  mixins: [pacProject],
  props: {
    section: {
      type: Object,
      required: true
    }
  },
  data () {
    return {
      newComment: this.defaultComment()
    }
  },
  methods: {
    defaultComment () {
      return {
        text: '',
        user: {
          id: this.$user.id,
          firstname: this.$user.user_metadata.firstname,
          lastname: this.$user.user_metadata.lastname
        }
      }
    },
    getCommentDate (comment) {
      return dayjs(comment.timestamp).format('DD/MM/YY hh:mm')
    },
    async saveNewComment () {
      const savedSection = {
        comments: this.section.comments || [],
        path: this.section.path
      }

      this.newComment.timestamp = Date.now()
      savedSection.comments.push(this.newComment)

      await this.savePacItem(savedSection)

      this.newComment = this.defaultComment
    }
  }
}
</script>

<style scoped>
.comments-row {
  max-height: 60vh;
  overflow: scroll;
}
</style>
