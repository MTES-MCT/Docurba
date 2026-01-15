import regions from '@/assets/data/Regions.json'

export default ({ app }, inject) => {
  const utils = {
    formatProcedureName (procedure, collectivite) {
      if (procedure.name) {
        return procedure.name
      }

      const isInter = procedure?.procedures_perimetres?.length > 1

      let collectivitePorteuse = collectivite
      if (
        isInter &&
        collectivite &&
        procedure.collectivite_porteuse_id !== collectivitePorteuse?.code
      ) {
        collectivitePorteuse = [
          ...collectivite.groupements,
          ...collectivite.membres
        ].find(e => e.code === procedure.collectivite_porteuse_id)
      }

      const parts = [
        procedure.type,
        procedure.numero,
        procedure.doc_type +
          (isInter ? 'i' : '') +
          (procedure.is_pluih ? 'H' : ''),
        collectivitePorteuse?.intitule ?? ''
      ].filter(Boolean)
      return parts.join(' ')
    },
    formatEventProfileToCreator (event) {
      if (event.profiles) {
        return this.formatProfileToCreator(event.profiles)
      } else if (event.from_sudocuh) {
        return { avatar: 'S', label: 'Sudocuh', color: '#3A3A3A', poste: 'Historique' }
      } else {
        return { avatar: 'D', label: 'Docurba', color: 'primary', poste: 'Système' }
      }
    },
    formatProfileToCreator (profile) {
      let creator = null
      if (profile.firstname && profile.lastname) {
        creator = { avatar: profile.firstname[0], label: `${profile.firstname} ${profile.lastname.toUpperCase()}`, poste: profile.poste, detailsPoste: profile.other_poste }
      } else if (profile.email) {
        creator = { avatar: profile?.email[0], label: `${profile.email}`, poste: profile?.poste, detailsPoste: profile?.other_poste }
      }
      creator.color = profile.side === 'etat' ? '#69DF97' : '#FA7659'
      creator.email = profile.email
      creator.side = profile.side
      creator.legacy_sudocu = profile.legacy_sudocu ?? false
      creator.id = profile.user_id
      creator.initiator = !!profile.initiator
      creator.profile = profile
      creator.region = profile.region
      return creator
    },
    // ⚠️ Les clefs sont a minima aussi utilisées pour Pipedrive et Brevo
    POSTES_ETAT: {
      ddt: 'DDT(M)/DEAL',
      dreal: 'DREAL'
    },
    ROLES_ETAT: {
      chef_unite: 'Chef·fe d\'unité/de bureau/de service et adjoint·e',
      redacteur_pac: 'Rédacteur·ice de PAC',
      suivi_procedures: 'Chargé·e de l\'accompagnement des collectivités',
      referent_sudocuh: 'Référent·e Sudocuh'
    },
    POSTES_COLLECTIVITE: {
      be: 'Bureau d\'études',
      elu: 'Collectivité, Élu·e',
      employe_mairie: 'Collectivité, Technicien·ne ou employé·e',
      agence_urba: 'Agence d\'urbanisme',
      autre: 'Autre'
    },
    POSTES_PPA: {
      region: 'Région'
    },
    formatPostes (profile) {
      let postes = []

      const POSTES = { ...this.POSTES_ETAT, ...this.POSTES_COLLECTIVITE, ...this.POSTES_PPA }
      if (profile.poste === 'region') {
        const region = regions.find(r => r.code.padStart(2, '0') === profile.region)
        postes.push(`${POSTES[profile.poste]} ${region.name}`)
      } else if (profile.poste !== 'autre') {
        postes.push(POSTES[profile.poste])
      }

      for (const poste of profile.detailsPoste ?? []) {
        postes.push(this.ROLES_ETAT[poste] ?? poste)
      }
      postes = postes.join(', ')
      if (profile.side == 'ppa') {
        postes = `${postes} (PPA)`
      }

      return postes
    }
  }
  inject('utils', utils)
}
