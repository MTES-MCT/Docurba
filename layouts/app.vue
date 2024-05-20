<template>
  <nuxt />
</template>

<script>
export default {
  async mounted () {
    const { data: roles } = await this.$supabase.from('github_ref_roles').select('*').match({
      role: 'admin',
      user_id: this.$user.id
    })

    const tallyScript = document.createElement('script')
    tallyScript.setAttribute('src', 'https://tally.so/widgets/embed.js')
    tallyScript.setAttribute('async', true)
    document.head.appendChild(tallyScript)

    window.TallyConfig = {
      formId: roles.length ? 'w2Bjpg' : 'wLzPGG',
      popup: {
        open: {
          trigger: 'time',
          ms: 50000
        },
        hideTitle: true,
        autoClose: 2000,
        showOnce: true,
        doNotShowAfterSubmit: true
      }
    }
  }
}
</script>
