<template>
  <nuxt />
</template>

<script>
export default {
  watch: {
    '$user.id' () {
      this.redirectUser()
    }
  },
  async mounted () {
    this.redirectUser()

    const { data: roles } = await this.$supabase.from('github_ref_roles').select('*').match({
      role: 'admin',
      user_id: this.$user.id
    })

    const recaptchaScript = document.createElement('script')
    recaptchaScript.setAttribute('src', 'https://tally.so/widgets/embed.js')
    recaptchaScript.setAttribute('async', true)
    document.head.appendChild(recaptchaScript)

    window.TallyConfig = {
      formId: roles.length ? 'w2Bjpg' : 'wLzPGG',
      popup: {
        open: {
          trigger: 'time',
          ms: 50000
        },
        hideTitle: true,
        autoClose: 2000,
        doNotShowAfterSubmit: true
      }
    }
  },
  methods: {
    redirectUser () {
      if (process.client && this.private && !this.$user.id) {
        this.$router.push('/')
      }
    }
  }
}
</script>
