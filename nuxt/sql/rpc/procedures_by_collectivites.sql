CREATE OR REPLACE FUNCTION procedures_by_collectivites(codes json)
RETURNS TABLE (
    departement text,
    unique_collectivites_count bigint
)
LANGUAGE sql
SECURITY DEFINER
AS $$
SELECT p.*, array_agg(pp.*) AS procedures_perimetres
    FROM procedures p
    JOIN procedures_perimetres pp ON p.id = pp.procedure_id
    WHERE p.id IN (
        SELECT procedure_id
        FROM procedures_perimetres
        WHERE collectivite_code IN (
            SELECT json_array_elements_text(codes)
        )
    ) GROUP BY p.id;
$$;
