CREATE OR REPLACE VIEW procedurePlanDetails AS
  SELECT pp.noseriecollectivite,
  pp.noserieprocedure,
  c.nomcollectivite,
  c.codecollectivite,
  c.sicompetenceplan,
  c.noserietypecollectivite,
  c.libtypecollectivite,
  c.codetypecollectivite
  FROM sudocu.procedureplan pp
  LEFT JOIN public.collectivitesdetails c ON c.noseriecollectivite = pp.noseriecollectivite;
