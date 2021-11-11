<template>
  <v-card>
    <v-card-title>
      {{ section.titre }}
    </v-card-title>
    <v-card-text>
      <v-row>
        <v-col v-for="(comment, i) in section.comments" :key="i" cols="12">
          {{ comment.text }}
        </v-col>
      </v-row>
    </v-card-text>
    <v-card-actions>
      <v-row>
        <v-col cols="12">
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
export default {
  props: {
    section: {
      type: Object,
      required: true
    }
  },
  data () {
    console.log(this.$user)

    return {
      newComment: {
        text: '',
        user: {
          id: this.$user.id,
          firstname: this.$user.user_metadata.firstname,
          lastname: this.$user.user_metadata.lastname
        }
      }
    }
  },
  methods: {
    saveNewComment () {
      console.log('Save new comment here', this.newComment)
    }
  }
}
</script>
