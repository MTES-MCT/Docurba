import departements from "../miscs/referentiels/departements.json" assert { type: "json" };

async function updatePerimeterStatus(config) {
  for (const departement of departements) {
    console.log(`Updating ${departement.code} ${departement.intitule}`);
    console.time(departement.code);
    await fetch(
      `https://nuxt3.docurba.incubateur.net/api/urba/procedures/perimetres/update?departementCode=${departement.code}`
    );
    console.timeEnd(departement.code);
  }
}

export { updatePerimeterStatus };
