<template>
  <v-dialog max-width="800px" :value="value" @input="$emit('input', $event)">
    <v-card>
      <v-card-title>
        <h3>Partager {{ project.name }}</h3>
      </v-card-title>
      <v-card-text class="mt-8">
        <v-combobox
          v-model="emailsInput"
          :search-input.sync="searchInput"
          :error-messages="error"
          :delimiters="[',', ' ']"
          filled
          multiple
          chips
          single-line
          label="Email, séparés par une virgule"
          class="emails-input"
          @input="error = null"
        >
          <template #append>
            <div class="action-container">
              <v-select
                v-model="rightInput"
                :items="rights"
                hide-details
                single-line
                solo
                flat
                class="right-select"
              />
              <v-btn color="primary" :loading="loading" @click="shareProject">
                Partager
              </v-btn>
            </div>
          </template>
        </v-combobox>

        <p v-if="sharings?.length">
          Partagé avec :
        </p>
        <div class="sharing-list">
          <div v-for="sharing in sharings" :key="sharing.id" class="sharing">
            <div class="sharing-user">
              <v-avatar class="sharing-user-avatar" :size="32" :color="colorFromString(sharing.user_email)">
                {{ sharing.user_email.slice(0, 1).toUpperCase() }}
              </v-avatar>
              <div class="sharing-user-email">
                {{ sharing.user_email }}
              </div>
            </div>
            <v-select
              :items="rights"
              :value="sharing.role"
              hide-details
              single-line
              solo
              flat
              @input="updateRole(sharing, $event)"
            >
              <template #append-item>
                <v-list-item @click="cancelSharing(sharing.user_email)">
                  <v-list-item-content>
                    <v-list-item-title :style="{ color: '#e10600' }">
                      Supprimer l'accès
                    </v-list-item-title>
                  </v-list-item-content>
                </v-list-item>
              </template>
            </v-select>
          </div>
        </div>
      </v-card-text>
    </v-card>

    <!-- <v-snackbar
      v-model="snackbar"
    >
      Une erreur est survenue à la creation de votre document.
      <template #action>
        <v-btn
          text
          @click="snackbar = false"
        >
          Fermer
        </v-btn>
      </template>
    </v-snackbar> -->
  </v-dialog>
</template>

<script>
import axios from 'axios'

const EMAIL_REGEX = /^[a-zA-Z0-9.!#$%&'*+/=?^_`{|}~-]+@[a-zA-Z0-9-]+(?:\.[a-zA-Z0-9-]+)*$/

export default {
  props: {
    value: {
      type: Boolean,
      default: false
    },
    project: {
      type: Object,
      required: true
    }
  },
  data () {
    return {
      searchInput: '',
      emailsInput: [],
      rightInput: 'read',
      rights: [
        { text: 'Lecture', value: 'read' },
        { text: 'Écriture', value: 'write' }
      ],
      error: null,
      sharings: [],
      loading: false
    }
  },
  watch: {
    project: {
      immediate: true,
      handler () {
        this.getSharings()
      }
    }
  },
  methods: {
    async getSharings () {
      const { data } = await this.$supabase.from('projects_sharing').select('*').eq('project_id', this.project.id)
      this.sharings = data
    },
    async shareProject () {
      if (this.searchInput?.length) {
        // hack to add the current input instead of clearing it
        this.emailsInput.push(this.searchInput)
        this.searchInput = ''
      }

      if (!this.emailsInput.length) {
        this.error = 'Veuillez entrer un e-mail'
        return
      }

      if (this.emailsInput.some(email => !EMAIL_REGEX.test(email))) {
        this.error = "L'adresse e-mail est invalide"
        return
      }

      this.error = null
      this.loading = true

      const newSharings = this.emailsInput.map((email) => {
        return {
          user_email: email.toLowerCase().trim(),
          project_id: this.project.id,
          shared_by: this.$user.id,
          role: this.rightInput
        }
      })

      const { data: savedSharings } = await this.$supabase.from('projects_sharing').insert(newSharings).select()

      axios.post('/api/projects/notify/shared', {
        sharings: newSharings,
        sharedByData: this.$user.user_metadata
      })

      this.emailsInput = []
      this.sharings.push(...savedSharings)
      this.loading = false
    },
    async cancelSharing (email) {
      this.sharings = this.sharings.filter(s => s.user_email !== email)
      await this.$supabase.from('projects_sharing').delete().match({
        user_email: email,
        project_id: this.project.id
      })
    },
    async updateRole (sharing, newRole) {
      const { data: updatedSharing, error } = await this.$supabase.from('projects_sharing').update({
        role: newRole
      }).eq('id', sharing.id).select()

      if (!error) {
        // TODO: Add a feedback here that the change is good.

        // eslint-disable-next-line no-console
        console.log(updatedSharing)
      } else {
        // eslint-disable-next-line no-console
        console.log(error)
      }
    },
    colorFromString (str) {
      let hash = 0
      for (let i = 0; i < str.length; i++) {
        hash = str.charCodeAt(i) + ((hash << 5) - hash)
      }
      let color = '#'
      for (let i = 0; i < 3; i++) {
        const value = (hash >> (i * 8)) & 0xFF
        color += ('00' + value.toString(16)).substr(-2)
      }
      return color
    }
  }
}
</script>

<style>
.emails-input > .v-input__control > .v-input__slot > .v-select__slot > .v-input__append-inner {
  margin: 0;
}

.action-container {
  display: flex;
  align-items: center;
  height: 54px;
}

.action-container .v-input__icon .v-icon {
  transform: none !important;
}

.right-select {
  margin: 0;
  padding: 0;
  width: 8rem;
}

.right-select .v-select__selections {
  padding: 0 !important;
}

.right-select > .v-input__control > .v-input__slot {
  background: none !important;
}

.right-select input {
  display: none;
}

.sharing-list {
  display: flex;
  flex-direction: column;
  gap: 1rem;
}

.sharing {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.sharing-user {
  display: flex;
  gap: 1rem;
  align-items: center;
}

.sharing-user-avatar {
  color: #fff;
}

.sharing-user-email {
  font-size: 1rem;
  color: var(--v-grey-darken2);
}

.sharing .v-input, .sharing .v-input__control, .sharing .v-input__slot {
  width: 8rem;
  max-width: 8rem;
}
</style>
