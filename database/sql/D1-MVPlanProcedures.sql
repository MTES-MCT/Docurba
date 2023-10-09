DROP materialized view distinct_procedures_events;
create materialized view distinct_procedures_events as
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
    MAX(codecollectivite) as codecollectivite
    from sudocu_procedure_events
    GROUP BY noserieprocedure
    ORDER BY MAX(dateevenement) DESC;
