DROP TABLE IF EXISTS public.sudocu_procedure_schema;
CREATE TABLE public.sudocu_procedure_schema AS
  SELECT ps.noseriecollectivite,
  ps.noserieprocedure,
  ps.nomschema,
  ps.datefinecheance,
  ps.coutschemaht,
  ps.coutschemattc,
  c.nomcollectivite,
  c.codecollectivite,
  c.sicompetenceplan,
  c.noserietypecollectivite,
  c.libtypecollectivite,
  c.codetypecollectivite,
  p.noserietypeprocedure,
  p.noserietypedocument,
  p.commentaireproc,
  pperim.perimetre
  FROM sudocu.procedureschema ps
   left join sudocu.procedure p on p.noserieprocedure = ps.noserieprocedure
  LEFT JOIN public.collectivitesdetails c ON c.noseriecollectivite = ps.noseriecollectivite
  left join public.sudocu_procedures_perimetres pperim on p.noserieprocedure = pperim.procedure_id;
