create or replace view
  procedurePlanDetails as
with
  voletqualiene as (
    select
      ene.noserieprocedure,
      jsonb_build_object(
        'eval_environmental',
        vq.sievaluationenvironnementale,
        'is_integ_loi_ene',
        vq.siintegrationdispoloiene,
        'is_environnement',
        ene.sienvironnement,
        'is_paysage',
        ene.sipaysage,
        'is_entree_ville',
        ene.sientreeville,
        'is_patrimoine',
        ene.sipatrimoine,
        'is_lutte_insalubrite',
        ene.silutteinsalubrite,
        'is_renouvel_urbain',
        ene.sirenouvellementurbain,
        'is_developpement',
        ene.sideveloppement,
        'is_peri_plafond_statmnt',
        ene.sinbrmaxairestationnement,
        'is_schema_amenagement',
        ene.sischemasamenagements,
        'is_schema_amenagement_ss_reg',
        vq.sisecteuramenagementsansreglement,
        'is_stecal',
        vq.sistecal,
        'nb_stecal',
        vq.nombrestecal,
        'is_densite_mini',
        ene.sidensitemin,
        'is_aire_stationment_max',
        vq.sinombremaxstationnement,
        'is_comm_electronique',
        ene.sisecteurcommunicationelectro,
        'is_renvoi_rnu',
        vq.sirenvoirnu,
        'is_obligation_aire_statmnt',
        vq.siobligationrealstationnement
      ) as volet_qualitatif
    from
      sudocu.loiene ene
      inner join sudocu.voletqualitatif vq on vq.noserieprocedure = ene.noserieprocedure
  )
select
  pp.noseriecollectivite,
  pp.noserieprocedure,
  pp.sipsmv,
  pp.sipdu,
  pp.siobligationpdu,
  pp.sipluiscot,
  pp.siplhpluih,
  pp.coutplanttc,
  pp.coutplanht,
  pp.nomprestaexterne,
  c.nomcollectivite,
  c.codecollectivite,
  c.sicompetenceplan,
  c.noserietypecollectivite,
  c.libtypecollectivite,
  c.codetypecollectivite,
  vq.volet_qualitatif
from
  sudocu.procedureplan pp
  left join public.collectivitesdetails c on c.noseriecollectivite = pp.noseriecollectivite
  left join voletqualiene vq on vq.noserieprocedure = pp.noserieprocedure;
