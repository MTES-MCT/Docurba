CREATE FUNCTION procedures_by_collectivites(codes json)
RETURNS SETOF record
AS $$

SELECT p.*, array_agg(pp.*) AS procedures_perimetres,
CASE
  WHEN count(topics) >= 1 THEN array_agg(distinct topics.display_name)
ELSE
  Null
END as topics,
CASE
  WHEN count(topics) >= 1 THEN any_value(topics.comment) filter(where topics.topic_id = 1)
ELSE
  Null
END as topics__other__comment
    FROM procedures p
    JOIN procedures_perimetres pp ON p.id = pp.procedure_id
    left join lateral (
		select cp.procedure_id, cp.topic_id, ct.display_name, cp.comment
		from core_proceduretopic cp
		inner join core_topic ct on cp.topic_id = ct.id
    ) as topics on topics.procedure_id = p.id
    WHERE p.id IN (
        SELECT procedure_id
        FROM procedures_perimetres
        WHERE collectivite_code IN (
            SELECT json_array_elements_text(codes)
        )
    ) GROUP BY p.id;
$$ LANGUAGE sql
SECURITY INVOKER;
