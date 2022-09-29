const express = require('express')
const app = express()
app.use(express.json())

const dayjs = require('dayjs')
const customParseFormat = require('dayjs/plugin/customParseFormat')
dayjs.extend(customParseFormat)
const _ = require('lodash')

const { createClient } = require('@supabase/supabase-js')
const supabase = createClient('https://ixxbyuandbmplfnqtxyw.supabase.co', process.env.SUPABASE_ADMIN_KEY)

// const cache = {}

app.get('/edits', async (req, res) => {
  // eslint-disable-next-line prefer-const
  let { data: deptEdits } = await supabase.from('pac_sections_dept').select('created_at')
  // eslint-disable-next-line prefer-const
  let { data: projectsEdits } = await supabase.from('pac_sections_project').select('created_at')

  // console.log(deptEdits, errDept)
  // console.log(projectsEdits, errProjects)

  deptEdits = _.groupBy(deptEdits, edit => dayjs(edit.created_at).format('MM/YY'))
  projectsEdits = _.groupBy(projectsEdits, edit => dayjs(edit.created_at).format('MM/YY'))

  const agregate = _.uniq(Object.keys(deptEdits).concat(Object.keys(projectsEdits))).map((month) => {
    return {
      month,
      value: (deptEdits[month] ? deptEdits[month].length : 0) + (projectsEdits[month] ? projectsEdits[month].length : 0)
    }
  }).sort((d1, d2) => {
    return dayjs(`01/${d1.month}`, 'DD/MM/YY') - dayjs(`01/${d2.month}`, 'DD/MM/YY')
  })

  res.status(200).send(agregate)
})

app.get('/projects', async (req, res) => {
  // eslint-disable-next-line prefer-const
  let { data: projects } = await supabase.from('projects').select('id, name, created_at')
  // eslint-disable-next-line prefer-const
  let { data: projectsEdits } = await supabase.from('pac_sections_project').select('created_at, project_id')

  projects = projects.filter(p => !p.name.toLowerCase().includes('test'))
  projects = projects.filter((p) => {
    const edits = projectsEdits.filter(e => e.project_id === p.id)

    return edits.length > 4
  })

  res.status(200).send({ nbProjects: projects.length })
})

app.get('/ddt', async (req, res) => {
  const { data: admins } = await supabase.from('admin_users_dept').select('user_email, created_at').eq('role', 'ddt')

  const nbAgents = _.uniqBy(admins, admin => admin.user_email).length - 5

  res.status(200).send({ nbAgents })
})

module.exports = app
