DROP materialized view IF EXISTS distinct_procedures_events;
create materialized view distinct_procedures_events as
    select sudocu_procedure_events.noserieprocedure,
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
    jsonb_agg(volet_qualitatif) as volet_qualitatif,
    bool_and(sipsmv) as is_scot,
    bool_and(sipsmv) as is_pluih,
    bool_and(sipsmv) as is_pdu,
    bool_and(sipsmv) as mandatory_pdu,
    MAX(libstatutevenement) as last_event_statut,
    MAX(sudocu_procedure_events.codecollectivite) as codecollectivite
    from sudocu_procedure_events
    LEFT JOIN procedureplandetails pp ON pp.noserieprocedure = sudocu_procedure_events.noserieprocedure
    GROUP BY sudocu_procedure_events.noserieprocedure
    ORDER BY MAX(dateevenement) DESC;
