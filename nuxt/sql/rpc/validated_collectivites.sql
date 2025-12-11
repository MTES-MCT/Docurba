CREATE OR REPLACE FUNCTION validated_collectivites(since date, departement text)
RETURNS TABLE (
    collectivite_code text,
    created_at timestamp,
    profile_id uuid,
    email text
)
LANGUAGE sql
AS $$
SELECT
	inn.*,
	pf.email
FROM
	(
		SELECT
			pv.collectivite_code,
			MIN(pv.created_at) AS created_at,
			MIN(pv.profile_id::text)::UUID AS profile_id
		FROM
			procedures_validations pv
		WHERE
			pv.created_at > since
			AND pv.departement = departement
		GROUP BY
			pv.collectivite_code
		ORDER BY
			pv.collectivite_code
	) AS inn
	LEFT JOIN profiles pf ON inn.profile_id = pf.user_id;
$$;
