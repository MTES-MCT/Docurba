<template>
  <v-container>
    <client-only>
      <v-row>
        <v-col cols="12">
          <div class="text-h1">
            Mon Profil
            <span v-if="$user.profile.side ==='state'">Etat</span>
            <span v-if="$user.profile.side ==='collectivite'">Territoire</span>
          </div>
        </v-col>
        <v-col v-if="error" cols="12">
          <v-alert type="error">
            {{ error }}
          </v-alert>
        </v-col>
      </v-row>

      <v-row v-if="$user.profile.side">
        {{ $user.profile }}
        <v-col cols="12">
          <validation-observer v-if="$user.profile.side ==='state'" ref="observerSignupEtat" v-slot="{ handleSubmit }">
            <form @submit.prevent="handleSubmit(updateProfile)">
              <OnboardingSignupForm v-model="userStateData" />
              <v-row>
                <v-col cols="12" class="d-flex justify-end">
                  <v-btn
                    depressed
                    tile
                    color="primary"
                    :loading="loading"
                    type="submit"
                    large
                  >
                    Sauvegarder
                  </v-btn>
                </v-col>
              </v-row>
            </form>
          </validation-observer>
          <validation-observer v-if="$user.profile.side ==='collectivite'" ref="observerSignupEtat" v-slot="{ handleSubmit }">
            <form @submit.prevent="handleSubmit(updateProfile)">
              <OnboardingSignupCollectiviteForm v-model="userData" update-censored />
              <v-row>
                <v-col cols="12" class="d-flex justify-end">
                  <v-btn
                    depressed
                    tile
                    color="primary"
                    :loading="loading"
                    type="submit"
                    large
                  >
                    Sauvegarder
                  </v-btn>
                </v-col>
              </v-row>
            </form>
          </validation-observer>
        </v-col>
      </v-row>
    </client-only>
  </v-container>
</template>

<script>
import { ValidationObserver } from 'vee-validate'

export default {
  name: 'Profile',
  components: {
    ValidationObserver
  },
  data () {
    return {
      toUpdateUser: {},
      loading: false,
      error: null,
      userStateData: {
        firstname: '',
        lastname: '',
        email: '',
        password: '',
        departement: null,
        poste: null,
        region: null
      }
    }
  },
  computed: {
    userData: {
      get () {
        // eslint-disable-next-line
          const { email, collectivite_id, departement, firstname, lastname, other_poste, poste, region, tel, ...rest } = this.$user.profile
        return { email, collectivite_id, departement, firstname, lastname, other_poste, poste, region, tel }
      },
      set (val) { this.toUpdateUser = val }
    }
  },
  methods: {
    async updateProfile () {
      try {
        this.loading = true
        console.log('BEFORE: ')
        const { error } = await this.$supabase.from('profiles').update({ ...this.userData }).eq('user_id', this.$user.profile.user_id)
        console.log('this.toUpdateUser: ', this.$user.profile.user_id)
        if (error) { throw new Error(error) }
      } catch (error) {
        console.log(error)
        this.error = error
      } finally {
        this.loading = false
      }
    }
  }
}
</script>
