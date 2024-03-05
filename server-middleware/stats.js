const express = require('express')
const app = express()
app.use(express.json())

const dayjs = require('dayjs')
const customParseFormat = require('dayjs/plugin/customParseFormat')
dayjs.extend(customParseFormat)
const _ = require('lodash')

const github = require('./modules/github/github.js')
const supabase = require('./modules/supabase.js')

const docurbaTeamIds = [
  '66a506fd-100c-44e3-bab0-252874d5482b',
  'c02a319e-a643-4a86-89a4-1afb90948aef',
  'bfa135a3-ce38-4c3b-8c92-6edd679f150c',
  '40a8b2f6-a99e-4045-acc7-fa55351aab6e',
  '8ef1e197-4b45-453a-8200-a150056ca826',
  '3be46d2d-a238-40b7-b075-9cfb60b3ab6f',
  'c423a586-62ad-4eb7-a07b-affbb1668c17',
  '5c03447a-132e-47c1-bb78-eeba77e26a1d',
  '5a57bd93-7364-4658-bc58-37bcaa720b23',
  '55ac66c8-f28a-4877-b937-e6aa89766752',
  '79e3d56a-89f4-410b-9166-8fbb4e997ce5',
  'b6af627a-420c-4a2e-98e7-2984f200d1e1',
  'fb144a50-c145-4c28-a03c-de65021add01',
  'b4a3e179-2a04-4032-a196-31c3ddb9b99b',
  'e7e6d0b2-7b55-43f6-bcd5-d3c3369052b4'
]

const departements = require('./Data/departements-france.json')

// const cache = {}

app.get('/projects', async (req, res) => {
  let { data: projects } = await supabase.from('projects')
    .select('id, name, created_at, owner, towns, trame')
    .not('owner', 'is', null)
    .is('from_sudocuh', null)

  projects = projects.filter((p) => {
    const name = p.name ? p.name.toLowerCase() : ''
    return !name.includes('test') && !name.includes('essai')
  })

  // const test = projects.filter(p => p.towns && p.towns.length && p.towns[0] && !p.towns[0].departementCode)
  // test.forEach((p) => {
  //   console.log(p.name, p.trame, p.towns[0])
  // })

  projects = projects.filter(p => p.towns && p.towns.length && p.towns[0] && p.trame)
  projects = projects.filter(p => !docurbaTeamIds.includes(p.owner))

  const projectsByDept = _.groupBy(projects, p => p.trame)
  const projectsByMonth = _.groupBy(projects, p => dayjs(p.created_at).format('MM/YY'))

  _.forEach(projectsByDept, (projects, dept) => { projectsByDept[dept] = projects.length })
  _.forEach(projectsByMonth, (projects, month) => { projectsByMonth[month] = projects.length })

  res.status(200).send({
    nbProjects: projects.length,
    byDept: projectsByDept,
    byMonth: projectsByMonth
  })
})

app.get('/fdr', async (req, res) => {
  const { count } = await supabase.from('doc_frise_events')
    .select('id, projects!inner(owner)', { count: 'exact', head: true })
    .filter('projects.owner', 'not.in', '(' + docurbaTeamIds.map(id => `"${id}"`).join(',') + ')')
    .is('from_sudocuh', null)

  res.status(200).send({
    nbEvents: count
  })
})

app.get('/ddt', async (req, res) => {
  let { data: admins } = await supabase.from('github_ref_roles').select('user_id, ref, created_at').eq('role', 'admin')

  admins = admins.filter(admin => !docurbaTeamIds.includes(admin.user_id))
  admins = _.uniqBy(admins, admin => admin.user_id)

  const nbAdmins = admins.length

  res.status(200).send({ nbAdmins, byDept: _.groupBy(admins, admin => admin.ref.replace('dept-', '')) })
})

const cachedDiff = { timestamp: 0 }
const hour = 60 * 60 * 1000

app.get('/diff', async (req, res) => {
  if (cachedDiff.timestamp > 0) {
    res.status(200).send(cachedDiff)
  }

  if (cachedDiff.timestamp + hour < Date.now()) {
    const changes = { }

    for (let index = 0; index < departements.length; index++) {
      const dept = departements[index]

      const basehead = `main...dept-${dept.code_departement}`

      const { data: diff } = await github(`GET /repos/{owner}/{repo}/compare/${basehead}`, {
        basehead,
        per_page: 10,
        page: 1
      })

      const nbChanges = diff.files.reduce((total, file) => {
        const nb = file.changes

        return total + (nb > 0 ? nb : 0)
      }, 0)

      changes[dept.code_departement] = nbChanges
    }

    const min = Object.values(changes).sort((a, b) => a - b)[0]

    console.log('Min changes', min)

    departements.forEach((dept) => {
      const code = dept.code_departement
      changes[code] -= min
    })

    changes.total = Object.values(changes).reduce((sum, val) => {
      return sum + val
    }, 0)

    changes.timestamp = Date.now()

    if (cachedDiff.timestamp === 0) {
      res.status(200).send(changes)
    }

    Object.assign(cachedDiff, changes)
  }

  // console.log(data)
})

module.exports = app
