CREATE OR REPLACE VIEW procedureSchemaDetails AS
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
  p.noprocedure
  FROM sudocu.procedureschema ps
  left join sudocu.procedure p on p.noserieprocedure = ps.noseriecollectivite
  LEFT JOIN public.collectivitesdetails c ON c.noseriecollectivite = ps.noseriecollectivite;
