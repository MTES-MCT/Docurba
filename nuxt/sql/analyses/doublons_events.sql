WITH event_groups AS (
    SELECT
        id,
        date_iso,
        type,
        procedure_id,
        CASE
            WHEN type IN ('Prescription', 'Délibération de prescription du conseil municipal', 'Délibération de l''établissement public qui prescrit', 'Délibération de prescription du conseil municipal ou communautaire') THEN 'Prescription_Group'
            WHEN type IN ('Délibération d''approbation', 'Approbation', 'Caractère exécutoire', 'Approbation du préfet', 'Retrait de l''annulation totale', 'Délibération d''approbation du municipal ou communautaire', 'Délibération d''approbation') THEN 'Approbation_Group'
            ELSE type
        END AS type_group
    FROM
        doc_frise_events
    WHERE
        type IN ('Prescription', 'Délibération de prescription du conseil municipal', 'Délibération d''approbation', 'Approbation')
        AND date_iso >= TO_CHAR(now() - INTERVAL '12 months', 'YYYY-MM-DD')
),
ranked_events AS (
    SELECT
        eg.*,
        ROW_NUMBER() OVER (
            PARTITION BY eg.procedure_id, eg.type_group
            ORDER BY eg.date_iso
        ) AS row_num
    FROM
        event_groups eg
)
SELECT
    e1.id AS id1,
    e2.id AS id2,
    e1.procedure_id,
    e1.type AS type1,
    e2.type AS type2,
    e1.type_group,
    e1.date_iso AS date1,
    e2.date_iso AS date2,
    (e2.date_iso::date - e1.date_iso::date) AS days_between
FROM
    ranked_events e1
JOIN
    ranked_events e2 ON e1.procedure_id = e2.procedure_id
    AND e1.type_group = e2.type_group
    AND e1.row_num < e2.row_num
    AND (e2.date_iso::date - e1.date_iso::date) < 2
ORDER BY
    e1.procedure_id, e1.type_group, e1.date_iso;
