# Jeu de données de test

Les jeux de données géographiques de tests utilisés sont ceux de l'INSEE (https://www.insee.fr/fr/information/2560452)

## Régions

```
cat v_region_2026.csv | cut -d ',' -f 1,6 | tr -d '"' > regions.csv
```

## Départements
```
cat v_departement_2026.csv | cut -d ',' -f 1,2,7 | tr -d '"' > departements.csv
```

## Communes

```
cat v_commune_2026.csv | grep -w 'COM' | cut -d ',' -f 2,4,10 | tr -d '"' > communes.csv
```
