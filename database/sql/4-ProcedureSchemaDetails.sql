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
  c.codetypecollectivite
  FROM sudocu.procedureschema ps
  LEFT JOIN public.collectivitesdetails c ON c.noseriecollectivite = ps.noseriecollectivite;