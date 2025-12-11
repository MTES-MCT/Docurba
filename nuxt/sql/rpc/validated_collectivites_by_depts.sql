CREATE OR REPLACE FUNCTION validated_collectivites_by_depts(since date)
RETURNS TABLE (
    departement text,
    unique_collectivites_count bigint
)
LANGUAGE sql
SECURITY DEFINER
AS $$
SELECT
	departement,
	COUNT(DISTINCT collectivite_code) AS unique_collectivites_count
FROM
	procedures_validations
WHERE
  created_at > since
GROUP BY
	departement
ORDER BY
	departement;
$$;
