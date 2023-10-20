DROP TABLE IF EXISTS public.sudocu_procedure_events;
CREATE TABLE public.sudocu_procedure_events AS
SELECT events.noserieevenement,
  events.noserieprocedureratt,
  events.libtypeevenement,
  events.codetypedocument,
  events.libtypedocument,
  events.dateevenement,
  events.noserieprocedure,
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
  ppcdetails.codecollectivite,
  ppcdetails.nomcollectivite,
  ppcdetails.sicompetenceplan,
  ppcdetails.noserietypecollectivite,
  ppcdetails.libtypecollectivite,
  ppcdetails.codetypecollectivite,
  ppcdetails.noserieprocedure as joinedpccid
FROM public.eventsdetails events
INNER JOIN public.procedureplandetails ppcdetails ON ppcdetails.noserieprocedure = events.noserieprocedure;
