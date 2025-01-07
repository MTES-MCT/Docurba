export default ({ app }, inject) => {
  const utils = {
    formatProcedureName (procedure, collectivite) {
      if (procedure.name) {
        return procedure.name
      }

      const isInter = procedure?.procedures_perimetres?.length > 1

      let collectivitePorteuse = collectivite
      if (isInter && collectivite?.intercommunaliteCode && collectivite?.groupements) {
        collectivitePorteuse = collectivite.groupements.find(e => e.code === collectivite.intercommunaliteCode)
      }

      return `${procedure.type} ${procedure.numero ?? ''} ${procedure.doc_type}${isInter ? 'i' : ''}${procedure.is_pluih ? 'H' : ''} ${collectivitePorteuse?.intitule ?? ''}`
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
      return creator
    },
    posteDetails (techName) {
      const map = {
        employe_mairie: 'Employé de mairie',
        redacteur_pac: 'Rédacteur de PAC',
        ddt: 'DDT',
        be: 'Bureau d\'étude',
        elu: 'Élu',
        autre: 'Autre',
        suivi_procedures: 'Suivi de procédure',
        referent_sudocuh: 'Référent Sudocuh',
        chef_unite: 'Chef d\'unité'
      }
      return map[techName] ?? techName
    }
  }
  inject('utils', utils)
}
