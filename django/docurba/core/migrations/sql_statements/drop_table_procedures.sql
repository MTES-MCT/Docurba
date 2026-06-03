ALTER TABLE ONLY public.versements
    DROP CONSTRAINT versements_procedure_id_fkey;

ALTER TABLE ONLY public.procedures_validations
    DROP CONSTRAINT procedures_validations_procedure_id_fkey;

DROP TABLE public.procedures;

DROP FUNCTION public.procedures_by_insee_codes;
DROP FUNCTION public.procedures_by_sudocuh_ids;
