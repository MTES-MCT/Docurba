CREATE OR REPLACE VIEW collectivitesDetails AS
  SELECT c.noseriecollectivite,
    c.datecreation,
    c.datechangementcollectivite,
    c.siepdissout,
    c.siinterdepartementale,
    tc.noserietypecollectivite,
    c.nomcollectivite,
    c.codecollectivite,
    tc.libtypecollectivite,
    c.sicompetenceplan,
    c.commentaire,
    tc.codetypecollectivite
  FROM  sudocu.collectivite c
  LEFT JOIN sudocu.typecollectivite tc ON c.noserietypecollectivite = tc.noserietypecollectivite;
