import { defineStore, storeToRefs } from 'pinia'
import { computed, ref, watch } from 'vue'
import { useSupabase } from '@/composables/useSupabase'
import type { User } from '@/data/User'

export const useAuthStore = defineStore('auth', () => {
  const initialized = ref(false)
  const token = ref<string | null>(null)
  const user = ref<User | null>(null)

  const headers = computed<HeadersInit | undefined>(() => token.value ? {
    Authorization: `Bearer ${token.value}`,
  } : undefined)
  const signedIn = computed<boolean>(() => !!token.value)

  function setInitialized(newInitialized: boolean) {
    initialized.value = newInitialized
  }

  function setToken(newToken: string | null) {
    token.value = newToken
  }

  function setUser(newUser: User | null) {
    user.value = newUser
  }

  return {
    headers,
    initialized,
    setInitialized,
    setToken,
    setUser,
    signedIn,
    token,
    user,
  }
})

export function useAuth() {
  const store = useAuthStore()
  const supabase = useSupabase()
  const { headers, initialized, signedIn, token, user } = storeToRefs(store)

  async function initialize() {
    if (initialized.value) return

    const { data } = await supabase.auth.getSession()

    store.setInitialized(true)

    if (!data.session) return

    store.setToken(data.session.access_token)
  }

  async function signIn(email: string, password: string) {
    const { data, error } = await supabase.auth.signInWithPassword({ email, password })

    if (error) return

    store.setToken(data.session.access_token)
  }

  async function signOut() {
    const { error } = await supabase.auth.signOut()

    if (error) return

    store.setToken(null)
  }

  watch(token, async (newToken) => {
    if (newToken === null) {
      return store.setUser(null)
    }
    try {
      const res = await fetch(`${import.meta.env.VITE_API_URL}/user`, {
        headers: headers.value,
      })
      const data = await res.json()

      store.setUser(data)
    } catch (err) {
      store.setUser(null)
    }
  })

  return {
    headers,
    initialize,
    initialized,
    signedIn,
    signIn,
    signOut,
    user,
  }
}
