CREATE OR REPLACE FUNCTION validated_collectivites_2024(department_param text)
RETURNS TABLE (
    collectivite_code text,
    created_at timestamp,
    profile_id uuid,
    email text
)
LANGUAGE sql
AS $$
SELECT inn.*, email
FROM (
    SELECT DISTINCT pv.collectivite_code,
    MIN(pv.created_at) as created_at,
    MIN(pv.profile_id::text)::uuid as profile_id
    FROM procedures_validations pv
    WHERE pv.created_at > '2024-06-01'
    AND pv.departement = department_param
    GROUP BY pv.collectivite_code, pv.procedure_id
    ORDER BY pv.collectivite_code
    ) as inn
    left join profiles pf on inn.profile_id = pf.user_id;
$$;
