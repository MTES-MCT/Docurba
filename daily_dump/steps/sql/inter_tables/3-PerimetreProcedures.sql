DROP TABLE IF EXISTS public.sudocu_procedures_perimetres;
CREATE TABLE public.sudocu_procedures_perimetres AS
SELECT pp.*,
CASE
  WHEN pp.code_collectivite_porteuse is not null THEN 'plan'
  ELSE null
END as procedure_scope
FROM(
  SELECT procedure.noserieprocedure as procedure_id,
  array_agg(c.codeinseecommune::text) as communes_insee,
  array_agg(c.libcommune::text) as name_communes,
  count(procedure.noserieprocedure) as nb_communes,
  MAX(ppd.codecollectivite) as code_collectivite_porteuse,
  MAX(ppd.nomcollectivite) as name_collectivite_porteuse,
  array_agg(jsonb_build_object('inseeCode', c.codeinseecommune, 'name', c.libcommune)) as perimetre,
  MAX(ppd.codetypecollectivite) as type_collectivite_porteuse
  FROM sudocu.communeprocedure cp
  LEFT JOIN sudocu.commune c ON c.noseriecommune = cp.noseriecommune
  LEFT JOIN sudocu.procedure procedure ON procedure.noserieprocedure = cp.noserieprocedure
  INNER JOIN (
    SELECT *
    FROM sudocu.procedureplan pp
    LEFT JOIN public.collectivitesDetails c ON pp.noseriecollectivite = c.noseriecollectivite
  ) ppd ON ppd.noserieprocedure = cp.noserieprocedure
  GROUP BY procedure.noserieprocedure
  ORDER BY nb_communes desc) pp;
