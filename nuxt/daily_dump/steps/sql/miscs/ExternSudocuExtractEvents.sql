select procs.*, p.from_sudocuh as rattache_procedure_id_sudocu, substring(procs.perimetre->0->>'inseeCode' from 1 for 2) as departement,
CASE
    WHEN JSONb_ARRAY_LENGTH(procs.perimetre) = 1 THEN
      procs.perimetre->0->>'inseeCode'
    ELSE
      procs.collectivite_porteuse_id
  END
  AS collectivite_porteuse_id

from (
  select
    p.id,
    p.from_sudocuh as id_procedure_sudocu,
    p.collectivite_porteuse_id,
    p.doc_type,
    p.current_perimetre as perimetre,
    events.type,
    events.date_iso,
    --p.created_at,
    p.secondary_procedure_of,
    p.is_principale,
    p.type as type_procedure
  from
    doc_frise_events events
    inner join procedures p on events.procedure_id = p.id
  where events.profile_id is not null
    and events.type is not null
    and events.type <> ''
    --and p.from_sudocuh is null
    --and events.date_iso >= '2023-12-01'
) as procs
left join procedures p on procs.secondary_procedure_of = p.id;

