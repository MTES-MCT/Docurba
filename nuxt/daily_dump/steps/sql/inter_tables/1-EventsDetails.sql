DROP materialized view IF EXISTS distinct_procedures_events;
DROP materialized view IF EXISTS distinct_procedures_schema_events;
DROP view IF EXISTS eventsdetails;
DROP view IF EXISTS procedureplandetails;
DROP view IF EXISTS procedureschemadetails;
DROP view IF EXISTS collectivitesdetails;
CREATE OR REPLACE VIEW eventsDetails AS
  SELECT procedure_typed.noserieevenement, procedure_typed.noserieprocedureratt,procedure_typed.codetypedocument,procedure_typed.libtypedocument, procedure_typed.libtypeevenement, procedure_typed.dateevenement, procedure_typed.codetypeevenement, procedure_typed.commentaire, procedure_typed.nomdocument, procedure_typed.libstatutevenement, procedure_typed.codestatutevenement, procedure_typed.noserieprocedure, procedure_typed.libtypeprocedure, procedure_typed.commentairedgd, procedure_typed.commentaireproc, procedure_typed.datelancement, procedure_typed.dateapprobation, procedure_typed.dateabandon, procedure_typed.dateexecutoire, procedure_typed.siprocedureprincipale
  FROM(
    SELECT p.noserieprocedure, p.noserieprocedureratt,  td.codetypedocument, td.libtypedocument, tp.libtypeprocedure, p.commentairedgd, p.commentaireproc, p.datelancement, p.dateapprobation, p.dateabandon, p.dateexecutoire, ev.noserieevenement, ev.dateevenement, ev.libtypeevenement, ev.codetypeevenement,  ev.commentaire, ev.nomdocument, ev.libstatutevenement, ev.codestatutevenement, tp.siprocedureprincipale
    FROM sudocu.procedure p
    INNER JOIN (
      SELECT e.noserieprocedure, e.noserieevenement, e.dateevenement, e.commentaire, e.nomdocument, te.libtypeevenement, te.codetypeevenement, se.libstatutevenement, se.codestatutevenement
      FROM sudocu.evenement e
      LEFT JOIN sudocu.typeevenement te ON te.noserietypeevenement = e.noserietypeevenement
      LEFT JOIN sudocu.statutevenement se ON se.noseriestatutevenement = e.noseriestatutevenement
    ) as ev ON ev.noserieprocedure = p.noserieprocedure
    LEFT JOIN sudocu.typeprocedure as tp ON tp.noserietypeprocedure = p.noserietypeprocedure
    LEFT JOIN sudocu.typedocument as td ON td.noserietypedocument = p.noserietypedocument
  ) as procedure_typed;
