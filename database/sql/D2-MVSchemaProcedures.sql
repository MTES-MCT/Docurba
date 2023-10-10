DROP materialized view IF EXISTS distinct_procedures_schema_events;
create materialized view distinct_procedures_schema_events as
select *
from(
    select noserieprocedure,
    MAX(dateevenement) as last_event_date,
    MAX(noserieevenement) as last_event_id,
    MAX(noserieprocedureratt) as noserieprocedureratt,
    MAX(libtypeevenement) as libtypeevenement,
    MAX(codetypedocument) as codetypedocument,
    MAX(libtypedocument) as libtypedocument,
    MAX(libtypeprocedure) as libtypeprocedure,
    MAX(commentairedgd) as commentairedgd,
    MAX(commentaireproc) as commentaireproc,
    MAX(datelancement) as datelancement,
    MAX(dateapprobation) as dateapprobation,
    MAX(dateabandon) as dateabandon,
    MAX(dateexecutoire) as dateexecutoire,
    MAX(commentaire) as commentaire,
    MAX(nomdocument) as nomdocument,
    MAX(libstatutevenement) as last_event_statut,
    MAX(spe.codecollectivite) as codecollectivite,
    MAX(nomschema) as nomschema,
    MAX(datefinecheance) as datefinecheance,
    MAX(coutschemaht) as coutschemaht,
    MAX(coutschemattc) as coutschemattc

    from sudocu_schemas_events spe
    GROUP BY spe.noserieprocedure
    ORDER BY MAX(spe.dateevenement) DESC
    ) ps;
