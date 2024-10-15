WITH date_range AS (
    SELECT
        TO_CHAR(NOW() - INTERVAL '12 months', 'YYYY-MM-DD') AS start_date,
        TO_CHAR(NOW(), 'YYYY-MM-DD') AS end_date
),
events_with_rank AS (
    SELECT
        procedure_id,
        date_iso,
        type,
        ROW_NUMBER() OVER (
            PARTITION BY procedure_id
            ORDER BY
                CASE
                    WHEN type != 'Autre' THEN 1
                    ELSE 2
                END,
                date_iso
        ) AS event_rank
    FROM doc_frise_events
    WHERE date_iso > (SELECT start_date FROM date_range)
      AND date_iso <= (SELECT end_date FROM date_range)
),
filtered_events AS (
    SELECT
        procedure_id,
        MIN(CASE WHEN event_rank = 1 THEN date_iso END) AS first_event_date,
        MIN(CASE WHEN event_rank = 1 THEN type END) AS first_event_type
    FROM events_with_rank
    GROUP BY procedure_id
),
procedures_with_perimeter AS (
    SELECT
        fe.procedure_id,
        fe.first_event_date,
        fe.first_event_type,
        p.doc_type,
        p.type AS procedure_type,
        p.from_sudocuh,
        ARRAY_AGG(pp.collectivite_code ORDER BY pp.collectivite_code) AS collectivite_codes
    FROM filtered_events fe
    JOIN procedures p ON fe.procedure_id = p.id
    JOIN procedures_perimetres pp ON p.id = pp.procedure_id
    GROUP BY fe.procedure_id, fe.first_event_date, fe.first_event_type, p.doc_type, p.type, p.from_sudocuh
),
potential_doublons AS (
    SELECT
        a.procedure_id AS procedure1,
        b.procedure_id AS procedure2,
        a.first_event_date AS date1,
        b.first_event_date AS date2,
        a.first_event_type AS event_type1,
        b.first_event_type AS event_type2,
        a.doc_type AS doc_type1,
        b.doc_type AS doc_type2,
        a.procedure_type AS procedure_type1,
        b.procedure_type AS procedure_type2,
        a.from_sudocuh AS from_sudocuh1,
        b.from_sudocuh AS from_sudocuh2,
        a.collectivite_codes AS collectivite_codes1,
        b.collectivite_codes AS collectivite_codes2,
        ABS(DATE(b.first_event_date) - DATE(a.first_event_date)) AS day_difference
    FROM procedures_with_perimeter a
    JOIN procedures_with_perimeter b ON a.procedure_id < b.procedure_id
    WHERE ABS(DATE(b.first_event_date) - DATE(a.first_event_date)) < 2
      AND a.doc_type = b.doc_type
      AND a.procedure_type = b.procedure_type
      AND a.collectivite_codes = b.collectivite_codes
      AND ((a.from_sudocuh IS NULL AND b.from_sudocuh IS NOT NULL) OR
           (a.from_sudocuh IS NOT NULL AND b.from_sudocuh IS NULL))
)
SELECT
    pd.procedure1 AS id1,
    pd.procedure2 AS id2,
    pd.doc_type1,
    pd.doc_type2,
    pd.procedure_type1,
    pd.procedure_type2,
    pd.from_sudocuh1,
    pd.from_sudocuh2,
    pd.collectivite_codes1,
    pd.collectivite_codes2,
    pd.collectivite_codes1 AS common_collectivite_codes,
    pd.date1,
    pd.date2,
    pd.event_type1,
    pd.event_type2,
    pd.day_difference
FROM potential_doublons pd
ORDER BY pd.day_difference, pd.date1
LIMIT 1000;
