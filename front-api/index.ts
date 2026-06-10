import { createClient } from '@supabase/supabase-js'
import cors from 'cors'
import type { Request, Response } from 'express'
import express from 'express'
import { decode } from 'jsonwebtoken'

import COMMUNES from './data/communes.json' with { type: 'json' }
import DEPARTEMENTS from './data/departements.json' with { type: 'json' }
import GROUPEMENTS from './data/groupements.json' with { type: 'json' }
import REGIONS from './data/regions.json' with { type: 'json' }

import type { Collectivite, Departement, Region } from './types.d.ts'
import { normalize } from './utils/normalize.ts'

const app = express()
const PORT = 5000
const SUPABASE_KEY = 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZS1kZW1vIiwicm9sZSI6ImFub24iLCJleHAiOjE5ODM4MTI5OTZ9.CRXP1A7WOeoJeXxjNni43kdQwgnWNReilDMblYTn_I0'
const SUPABASE_URL = 'http://127.0.0.1:54321'

app.use(cors())
app.use(express.json())

app.use((req, _res, next) => {
  console.log(req.url)

  next()
})

// Auth

app.get('/user', async (req, res) => {
  const supabase = getSupabase(req)
  const userId = getUserId(req)

  if (!userId) {
    return res.status(401).send()
  }

  const { data } = await supabase.from('profiles')
    .select('*')
    .eq('user_id', userId)
    .limit(1)
    .single()

  return data
    ? res.send({
      departementId: data.departement || null,
      email: data.email,
      firstname: data.firstname,
      government: data.side === 'etat',
      id: userId,
      lastname: data.lastname,
      regionId: data.region || null,
      scope: parseUserScope(data.poste, data.side),
    })
    : res.status(401).send()
})

// Collectivités

const collectivites = [
  ...(COMMUNES as Array<Collectivite>),
  ...(GROUPEMENTS as Array<Collectivite>),
].sort((a, b) => normalize(a.name) > normalize(b.name) ? 1 : -1)
const collectivitesNameById: Record<string, string> = {}
collectivites.forEach((collectivite) => {
  collectivitesNameById[collectivite.id] = collectivite.name
})

app.get('/collectivites', (req, res) => {
  const filters: Array<(collectivite: Collectivite) => boolean> = []

  if (req.query.id) {
    const ids = Array.isArray(req.query.id)
      ? req.query.id
      : [req.query.id]

    filters.push((collectivite) => ids.includes(collectivite.id))
  }
  if (req.query.departement) {
    filters.push((collectivite) => collectivite.departementId === req.query.departement)
  }

  return filters.length
    ? paginate(
        req,
        res,
        collectivites.filter(
          (collectivite) => filters.every((filter) => filter(collectivite))
        ),
      )
    : res.status(404).send()
})

app.get('/collectivites/:collectiviteId', (req, res) =>
  res.send(collectivites.find(
    (collectivite) => collectivite.id === req.params.collectiviteId
  ) ?? null)
)

// Départements

const departements = DEPARTEMENTS as Array<Departement>

app.get('/departements', (req, res) =>
  paginate(req, res, departements)
)

app.get('/departements/:departementId', (req, res) =>
  res.send(departements.find(
    (departement) => departement.id === req.params.departementId
  ) ?? null)
)

// Procédures

app.get('/procedures', async (req, res) => {
  if (!req.query.collectivite && !req.query.departement) {
    return res.status(404).send()
  }

  const supabase = getSupabase(req)
  let proceduresQuery = supabase.from('procedures_perimetres')
    .select('*, procedures!inner(*,doc_frise_events(*))')
    .is('procedures.archived', false)
    .neq('procedures.status', null)

  if (req.query.collectivite) {
    proceduresQuery = proceduresQuery.eq('collectivite_code', req.query.collectivite)
  }
  if (req.query.departement) {
    proceduresQuery = proceduresQuery.eq('departement', req.query.departement)
  }

  const { data, error } = await proceduresQuery

  if (error) {
    return res.status(401).send(error)
  }

  const procedures = data.map((d) => ({
    // TODO :: Get this
    approvalDate: null,
    children: [],
    collectiviteId: d.collectivite_code,
    documentType: parseDocumentType(d.procedures.doc_type),
    events: (d.procedures.doc_frise_events as Array<any>).map((e) => ({
      date: e.date_iso,
      description: e.description || null,
      id: e.id,
      type: parseEventType(e.type),
    })).sort((a, b) =>
      a.date === b.date
        ? 0
        : a.date > b.date
          ? -1
          : 1
    ),
    id: d.procedure_id,
    number: d.procedures.numero,
    parentId: d.procedures.secondary_procedure_of,
    // TODO :: Get this
    prescriptionDate: null,
    status: parseProcedureStatus(d.procedures.status),
    type: parseProcedureType(d.procedures.type),
    // TODO :: Remove this
    raw: d,
  }))
  const proceduresByParentId: Record<string, Array<any>> = {
    'null': [],
  }
  procedures.forEach((procedure) => {
    const parentId = procedure.parentId ?? 'null'

    if (proceduresByParentId[parentId]) {
      proceduresByParentId[parentId].push(procedure)
    } else {
      proceduresByParentId[parentId] = [procedure]
    }
  })

  return paginate(req, res, proceduresByParentId.null.map((procedure) => ({
    ...procedure,
    children: proceduresByParentId[procedure.id] ?? [],
  })).sort((a, b) => {
    const aCollectiviteName = collectivitesNameById[a.collectiviteId]
    const bCollectiviteName = collectivitesNameById[b.collectiviteId]

    return aCollectiviteName === bCollectiviteName
      ? 0
      : aCollectiviteName > bCollectiviteName
        ? 1
        : -1
  }))
})

app.get('/procedures/:procedureId', async (req, res) => {
  const supabase = getSupabase(req)
  const procedurePromise = supabase.from('procedures_perimetres')
    .select('*, procedures!inner(*,doc_frise_events(*))')
    .eq('procedures.id', req.params.procedureId)
    .limit(1)
    .single()
  const childrenPromise = supabase.from('procedures_perimetres')
    .select('*, procedures!inner(*,doc_frise_events(*))')
    .eq('procedures.secondary_procedure_of', req.params.procedureId)
    .is('procedures.archived', false)
    .neq('procedures.status', null)

  const [
    { data, error },
    { data: childrenData, error: childrenError },
  ] = await Promise.all([procedurePromise, childrenPromise])

  if (!data || error || !childrenData || childrenError) {
    return res.status(401).send(error)
  }

  const [procedure, ...children] = [data, ...childrenData].map((d) => ({
    // TODO :: Get this
    approvalDate: null,
    children: [],
    collectiviteId: d.collectivite_code,
    documentType: parseDocumentType(d.procedures.doc_type),
    events: (d.procedures.doc_frise_events as Array<any>).map((e) => ({
      date: e.date_iso,
      description: e.description || null,
      id: e.id,
      type: parseEventType(e.type),
    })).sort((a, b) =>
      a.date === b.date
        ? 0
        : a.date > b.date
          ? -1
          : 1
    ),
    id: d.procedure_id,
    number: d.procedures.numero,
    parentId: d.procedures.secondary_procedure_of,
    // TODO :: Get this
    prescriptionDate: null,
    status: parseProcedureStatus(d.procedures.status),
    type: parseProcedureType(d.procedures.type),
    // TODO :: Remove this
    raw: d,
  }))

  return res.send({
    ...procedure,
    children,
  })
})

// Régions

const regions = REGIONS as Array<Region>

app.get('/regions', (req, res) =>
  paginate(req, res, regions)
)

// Listener

app.listen(PORT, () => {
  console.log(`Server running on port ${PORT}`)
})

// Utils

function getSupabase(req: Request) {
  return createClient(SUPABASE_URL, SUPABASE_KEY, {
    accessToken: async () => getToken(req)
  })
}

function getToken(req: Request) {
  return req.headers.authorization?.split(' ')[1] ?? null
}

function getUserId(req: Request) {
  const token = getToken(req)

  if (!token) {
    return null
  }

  const decodedToken = decode(token)

  return decodedToken ? String(decodedToken.sub) : null
}

function paginate<T>(req: Request, res: Response, results: Array<T>) {
  const page = parseQueryNumber(req.query.page, 1)
  const size = parseQueryNumber(req.query.size, 0)

  res.send({
    count: results.length,
    results: size
      ? results.slice((page - 1) * size, page * size)
      : results,
  })
}

function parseDocumentType(value: string | null) {
  switch (value) {
    case 'CC':
      return 'CC'
    case 'PLU':
    case 'POS':
      return 'PLU'
    case 'PLUi':
      return 'PLUI'
    case 'PLUiH':
      return 'PLUIH'
    case 'PLUiHM':
      return 'PLUIHM'
    case 'PLUiM':
      return 'PLUIM'
    case 'SCOT':
    case 'SD':
      return 'SCOT'
    default:
      return null
  }
}

function parseEventType(value: string | null) {
  switch (value) {
    case 'Abandon':
      return 'ABAND'
    case 'Affichage':
      return 'AFF'
    case 'Annulation TA':
      return 'ANNULTA'
    case 'Approbation du préfet':
      return 'APPPREF'
    case 'Arrêt de projet':
      return 'ARRPROJ'
    case 'Arrêté d\'abrogation':
      return 'ARRABRO'
    case 'Arrêté de lancement de la procédure':
      return 'ARRLANC'
    case 'Arrêté d\'enquête publique':
      return 'ARRENQ'
    case 'Arrêté du Maire ou du Préfet ou de l\'EPCI':
      return 'ARRMP'
    case 'Autre':
      return 'AUTRE'
    case 'Avis de l\'autorité environnementale':
      return 'AVISENV'
    case 'Avis de l\'État':
      return 'AVISETAT'
    case 'Avis de la CDNPS':
      return 'AVICDNPS'
    case 'Avis de la CDPENAF':
      return 'AVICDPENAF'
    case 'Caducité':
      return 'CADUC'
    case 'Caractère exécutoire':
      return 'EXECUT'
    case 'Consultation de l\'autorité environnementale (cas par cas)':
      return 'CONSENVCPC'
    case 'Consultation de l\'autorité environnementale':
      return 'CONSENV'
    case 'Consultation des PPA':
      return 'CONSPPA'
    case 'Débat sur le PADD en conseil communautaire et en conseils communaux':
      return 'DEBATEPADD'
    case 'Débat sur le PADD en conseil municipal':
    case 'Débat sur le PADD ou PAS':
    case 'Débat sur les orientations du PAS':
      return 'DEBPADD'
    case 'Début de mise à disposition du public':
      return 'DEBINFO'
    case 'Début d\'enquête publique':
      return 'DEBENQ'
    case 'Délibération d\'approbation':
    case 'Délibération d\'approbation du conseil municipal ou communautaire':
      return 'DELAPP'
    case 'Délibération de bilan de la concertation':
      return 'DELBILAN'
    case 'Délibération décidant de la mise en compatibilité':
      return 'DELMEC'
    case 'Délibération de l\'Etab Pub sur les modalités de concertation':
    case 'Délibération de l\'Etablissement Public':
    case 'Délibération de l\'établissement public qui prescrit':
    case 'Délibération de prescription du conseil municipal ou communautaire':
    case 'Délibération de prescription du conseil municipal':
    case 'Prescription':
      return 'PRES'
    case 'Délibération objectifs et modalités concertation':
      return 'DELOMC'
    case 'Dérogation au titre du L142-4 (ex L122-2)':
      return 'DEROG'
    case 'Exemption évaluation environnementale':
      return 'EXEMEVALENV'
    case 'Fin d\'échéance':
      return 'ECHSCH'
    case 'Fin de mise à disposition du public':
      return 'FININFO'
    case 'Fin d\'enquête publique':
      return 'FINENQ'
    case 'Notification de modification(préfet, CR, CG...)':
      return 'NOTMOD'
    case 'Notification du projet ou demande de DUP':
      return 'NOTPROJ'
    case 'Porter à connaissance':
    case 'Transmission du porter-à-connaissance':
      return 'PAC'
    case 'Porter à connaissance complémentaire':
    case 'Transmission du porter à connaissance complémentaire':
      return 'PACCOMP'
    case 'Publication':
      return 'PUB'
    case 'Publication périmètre':
      return 'PUBPERI'
    case 'Publicité dans la presse':
      return 'ADSPRESS'
    case 'Recours gracieux de l\'État':
      return 'RECGRAC'
    case 'Retrait de la délibération d\'approbation':
      return 'BACKAPPROB'
    case 'Réunion des PPA':
    case 'Réunion des PPA sur le diagnostic':
      return 'REUPPA'
    case 'Saisine de la CDNPS pour avis':
      return 'CONSCDNPS'
    case 'Transmission au contrôle de légalité':
      return 'TRANSCONT'
    case 'Transmission au préfet pour approbation':
      return 'TRPREFAPP'
    default:
      return null
  }
}

function parseProcedureStatus(value: string | null) {
  switch (value) {
    case 'abandon':
      return 'ABANDONNEE'
    // case 'Abrogee':
    //   return 'ABROGEE'
    case 'annule':
      return 'ANNULEE'
    // case 'Approuvee':
    //   return 'APPROUVEE'
    case 'caduc':
      return 'CADUC'
    case 'en cours':
      return 'EN_COURS'
    // case 'EnProjet':
    //   return 'EN_PROJET'
    case 'opposable':
      return 'OPPOSABLE'
    // case 'Precedente':
    //   return 'PRECEDENTE'
    default:
      return null
  }
}

function parseProcedureType(value: string | null) {
  switch (value) {
    case 'Abrogation':
      return 'ABROGATION'
    case 'Elaboration':
      return 'ELABORATION'
    case 'Mise à jour':
      return 'MISE_A_JOUR'
    case 'Mise en compatibilité':
      return 'MISE_EN_COMPATIBILITE'
    case 'Modification':
      return 'MODIFICATION'
    case 'Révision allégée (ou RMS)':
      return 'REVISION_ALLEGEE'
    case 'Modification simplifiée':
      return 'MODIFICATION_SIMPLIFIEE'
    case 'Révision':
      return 'REVISION'
    case 'Révision simplifiée':
      return 'REVISION_SIMPLIFIEE'
    default:
      return null
  }
}

function parseQueryNumber(value: any, defaultValue: number = 0) {
  const number = Number(value)

  return Number.isNaN(number) ? defaultValue : number
}

function parseUserScope(poste: string | null, side: string) {
  switch (poste) {
    case null:
      return side === 'etat'
        ? 'ETAT'
        : side === 'ppa'
          ? 'REGION'
          : 'COLLECTIVITE'
    case 'agence_urba':
    case 'autre':
    case 'be':
    case 'elu':
    case 'employe_mairie':
      return 'COLLECTIVITE'
    case 'ddt':
      return side === 'etat'
        ? 'ETAT'
        : side === 'ppa'
          ? 'REGION'
          : 'COLLECTIVITE'
    case 'dreal':
    case 'region':
      return 'REGION'
    default:
      return null
  }
}
