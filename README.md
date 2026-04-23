# Docurba

Cette documentation est en cours de création. Merci de l'agrémenter selon vos besoins.

##  Architecture

(à faire)

###  Base de données

La base de données est gérée par [Supabase](https://supabase.com/docs). En local, la CLI supabase permet de créer une base de données et un environnement local équivalent à la production. Malheureusement, Supabase ne permet pas de travailler avec plusieurs bases de données localement. Pourtant, il nous faut bien deux bases de données pour faire tourner les tests.
Jusqu'à maintenant, la base de données de test était créée par Pytest et utilisait donc l'URL `DATABASE_URL` configurée localement. Une nouvelle base était créée mais elle ne contenait pas :
- les spécificités de Supabase : roles, schémas, fonctions et extensions (notamment).
- la structure de la base de données de production qui est bien plus complet que les modèles Django. Il y a les tables mais aussi des fonctions, des déclencheurs et autres réjouissances créées en clic-clic-clic et non documentées.

Cela devient un véritable problème depuis que nous utilisons les migrations Django pour gérer les changements de structure. En effet, ceux-ci se basent sur des tables qui existent bien en production mais pas dans l'environnement de test.

Une première solution avait été de créer les tables manquantes dans un `conftest.py`. Puis via des signaux spécifiques à chaque application Django mais tout cela était incomplet. Maintenant, il est temps d'utiliser la structure complète de la base de données pour travailler sereinement.

#### Locale

Voir `supabase start`.

#### Test

En résumé :
- Docker compose expose une base de test qui s'appuie sur l'image officielle de Supabase.
- Le schéma de production est injecté dans la base de test lorsqu'elle est disponible.
- Les migrations Django sont exécutées ensuite.
- Puis Pytest peut tourner gentiment sans râler.
La tâche  `mise start:tests` permet de lancer l'ensemble automatiquement. Elle est utilisée dans la CI et peut être lancée localement.

#####  Docker compose à la rescousse
La base de données de test utilise l'image officielle de Supabase qui est documentée dans la partie « [self-hosting with Docker](https://supabase.com/docs/guides/self-hosting/docker) ». Elle s'appuie sur les valeurs d'environnement `PG*`.
Les scripts spécifiques sont dans le dossier `docker`.
La structure spécifique à Supabase est ainsi créée par l'image mais aussi par des scripts qui ont été écrits par eux (voir le dossier `docker/test_db/supabase_seeds`) et qui viennent du dépôt officiel.

#####  Schéma de production

Voir `docker/test_db/prod_schema_before_django_migrations.sql`.
Le schéma de production a été créé avec `pg_dump` puis nettoyé et adapté. Il contient les tables, les fonctions, les extensions, certains déclencheurs et les permissions.
Plus les modèles Django refléteront la structure de la base, moins nous aurons besoin de ce fichier. In fine, il pourra être supprimé lorsque tout aura été « traduit » dans Django.

##  Environnement local

### Installation des outils
- Installer [uv](https://docs.astral.sh/uv/getting-started/installation/) : Gestion des versions Python, dépendances et environnements virtuels
- Installer [nvm](https://www.nvmnode.com/guide/download.html) : Gestion des versions Node et dépendances
- Installer [direnv](https://direnv.net/#basic-installation) : Gestion des variables d'environnement locales
- Installer [Supabase](https://supabase.com/docs/guides/local-development/cli/getting-started)
- Installer [Docker](https://docs.docker.com/engine/install/)
- Installer le client [PostgreSQL](https://www.postgresql.org/download/)

Example sous fedora :

```
sudo dnf install uv direnv postgresql https://github.com/supabase/cli/releases/download/v2.93.1/supabase_2.93.1_linux_amd64.rpm
curl -o- https://raw.githubusercontent.com/nvm-sh/nvm/v0.39.5/install.sh | bash
```

### Cloner le dépôt Nuxt 3

- Clôner [le dépôt Nuxt 3](https://github.com/betagouv/docurba-nuxt3/) et renseigner la variable d'environnement NUXT3_PATH avec le chemin du dépôt clôné :

```
cd .. && git clone git@github.com:betagouv/docurba-nuxt3.git && cd -
```

### Configuration direnv

Copier les fichiers `.env.example` vers `.envrc` et autoriser direnv à y accéder :

```
cd nuxt && cp .env.example .envrc && direnv allow && cd -
cd django && cp .env.example .envrc && direnv allow && cd -
cd ${NUXT3_PATH} && cp .env.example .envrc && direnv allow && cd -
```

Pour éviter d'avoir à utiliser `direnv allow` à chaque modification de `.envrc`, modifier la config direnv comme suit :

```
mkdir -p ~/.config/direnv
cat >> ~/.config/direnv/direnv.toml <<EOF
[whitelist]
prefix = [ "/path/to/docurba-nuxt3", "/path/to/Docurba" ]
EOF
```

### Installer les dépendances

```
make install
```

### Lancer les applications

```
make start
```

### Makefile

Se référer au Makefile pour voir les différentes options d'installation et de lancement
