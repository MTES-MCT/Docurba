DROP TABLE IF EXISTS public.sudocu_schemas_events;
CREATE TABLE public.sudocu_schemas_events AS
SELECT events.noserieevenement,
  events.noserieprocedureratt,
  events.libtypeevenement,
  events.codetypedocument,
  events.libtypedocument,
  events.codetypeevenement,
  events.dateevenement,
  events.libtypeprocedure,
  events.commentairedgd,
  events.commentaireproc,
  events.datelancement,
  events.dateapprobation,
  events.dateabandon,
  events.dateexecutoire,
  events.commentaire,
  events.nomdocument,
  events.libstatutevenement,
  events.codestatutevenement,
  psdetails.*
FROM public.eventsdetails events
INNER JOIN public.procedureSchemaDetails psdetails ON psdetails.noserieprocedure = events.noserieprocedure;
