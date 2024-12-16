CREATE OR REPLACE FUNCTION validated_collectivites_by_depts_2024()
RETURNS TABLE (
    departement text,
    unique_collectivites_count bigint
)
LANGUAGE sql
SECURITY DEFINER
AS $$
    SELECT
        departement,
        COUNT(DISTINCT collectivite_code) as unique_collectivites_count
    FROM
        procedures_validations
    WHERE
        departement IS NOT NULL
        AND created_at >= '2024-06-01'
    GROUP BY
        departement
    ORDER BY
        departement;
$$;
