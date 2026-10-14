# Démarrage local

## Backend
```bash
python -m venv .venv && .venv/Scripts/activate      # Windows
pip install -r requirements.txt
cp backend/.env.example backend/.env                  # puis éditer les secrets
python backend/manage.py migrate
python backend/manage.py seed_demo                    # données FICTIVES
python backend/manage.py createsuperuser              # compte administrateur réel
python backend/manage.py runserver                    # http://localhost:8000/api/docs/
python backend/manage.py test
```
Par défaut SQLite ; pour PostgreSQL : `docker compose up -d db` puis `DB_ENGINE=postgres` dans `backend/.env`.

## Frontend
```bash
cd frontend
cp .env.example .env.local
npm install
npm run dev        # http://localhost:3000
npm run build
```

## Comptes de démonstration (après `seed_demo`, développement uniquement)
`demo.tech@example.test` (Technicien) et `demo.resp@example.test` (Responsable SAV).
Mot de passe défini dans `backend/inventory/management/commands/seed_demo.py` : à ne jamais utiliser en production.

## Avant un déploiement
- `DJANGO_DEBUG=False`, `DJANGO_SECRET_KEY` long et aléatoire, `DJANGO_ALLOWED_HOSTS`, `CORS_ALLOWED_ORIGINS`.
- PostgreSQL, HTTPS, stockage des médias, sauvegardes.
- Supprimer les comptes `demo.*`.
- `CORS_ALLOWED_ORIGINS` doit contenir l'origine exacte du frontend (cookies avec credentials) ; servir front et API en HTTPS sur le même domaine parent.
- Limites connues : cache de limitation de débit local à chaque processus (utiliser Redis en multi-instances), pas d'application mobile.
