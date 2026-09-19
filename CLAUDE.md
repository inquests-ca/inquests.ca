# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project overview

A Django + Django REST Framework rebuild of inquests.ca, a searchable database of Canadian inquest findings and legal authorities (case law, procedures, death-prevention references). The Django app lives in `app/`; the project is managed with `uv` (see `pyproject.toml` / `uv.lock`, Python 3.13).

## Development commands

All commands below assume `app/` as the working directory unless noted, and are run via `uv run python manage.py <command>` (or plain `python manage.py <command>` inside the Docker container, where the venv is already active).

### Running the app (Docker — recommended)

```
docker compose -f docker/docker-compose.yml up --build
```

This starts Postgres, then the entrypoint (`docker/docker-entrypoint.sh`) runs `migrate`, creates a superuser (`admin` / `admin@inquests.ca`, password from `DJANGO_SUPERUSER_PASSWORD` in `docker/.env.dev`), and starts `runserver 0.0.0.0:8000`. The repo's `data/` directory is mounted into the container at `/usr/src/data/`.

### Running locally without Docker

Django reads `POSTGRES_DB`, `POSTGRES_USER`, `POSTGRES_PASSWORD`, `POSTGRES_HOST`, `POSTGRES_PORT` from the environment with no defaults (`project/settings.py`), so they must be exported first (see `docker/.env.dev` for dev values; use `POSTGRES_HOST=localhost` if Postgres isn't in Docker).

```
uv run python manage.py migrate
uv run python manage.py runserver
```

### Data import

Source CSVs (FileMaker/Knack exports) live in `data/`. Import logic is a plain Python package at `app/importdata/` (not a Django app), with one `import_<model>(data: dict) -> Optional[Model]` function per file, each taking a CSV row dict and either creating a model instance or returning `None` to skip the row. Two management commands (`common/management/commands/`) share the `IMPORT_FUNCTIONS` mapping defined in `import_all.py`, which is ordered so FK dependencies (e.g. `inquest_document` needs `inquest` first) import correctly:

```
# Import everything, in dependency order, from data/ (or /usr/src/data/ in Docker)
uv run python manage.py import_all

# Import a single table; defaults to the same data/ path, or pass an override
uv run python manage.py import_table <import_type> [csv_path]
```

Row-level failures don't abort the run: `ValueError`/`django.db.DataError` raised by an import function is caught, logged as a warning, and counted, so partial/bad CSV rows are skipped rather than failing the whole import.

### Migrations

```
uv run python manage.py makemigrations
uv run python manage.py migrate
```

### Tests

```
uv run python manage.py test
```

No tests are currently written (each app has an empty `tests.py` stub).

### Admin

Django admin is available at `/admin/`; all models are registered per-app in `admin.py`.

## Architecture

### App layout

- `common/` — cross-cutting concerns: the `Jurisdiction` model (shared by both `inquests` and `authorities`), shared list-view mixins (`views.py`), and `base.html` / `registration/login.html` templates. Also owns the `import_all` / `import_table` management commands.
- `inquests/` — `Inquest` and everything scoped to it: documents, deceased persons, keywords, groups, presiding-officer/participant roles, recommendation recipients (`Party`/`PartyType`).
- `authorities/` — `Authority` (case law / legal authorities) and its documents, keywords, groups, levels, and citation graph.
- `importdata/` — CSV → model import functions (see Data import above). Not a Django app; imported directly by the management commands.
- `project/` — Django settings/urls/wsgi/asgi.

### Data model notes

- **Lookup-style models** (`InquestKeyword`, `AuthorityKeyword`, `Role`, `Party`) share a convention: a `name` field that can be blank plus a `category`/`party_type` field, with a `UniqueConstraint` on `Lower(name) + category`. `__str__` falls back to the category's display label when `name` is blank. When extending these, follow the same shape rather than introducing a different pattern.
- **`Inquest.presiding_officer`** is a FK to `Participant` (a general person record with M2M `roles`), not a dedicated "presiding officer" model. `Inquest.clean()` enforces that the linked `Participant` has a `Role` with `category=Role.Category.POI` — this is an application-level check (via `full_clean()`), not a DB constraint, since Django can't express a cross-table check constraint declaratively.
- **`Authority.level`** is a read-only `@property`, not a stored field — it's derived from the highest-ranked `AuthorityDocument.level` related to that authority (an authority can have documents from multiple court levels, e.g. as a case is appealed). `AuthorityDocument.jurisdiction` is likewise separate from `Authority.jurisdiction`, since a single authority's documents can span jurisdictions (e.g. an SCC ruling on a case that originated in a specific province).
- **`Authority.citations`** is a self-referential, asymmetrical M2M (`related_name='cited_by'`) — `authority.citations` = authorities this one cites, `authority.cited_by` = authorities that cite this one.
- **`Inquest.import_metadata`** is a normalized (lowercased) case-name key set during import and used to match `Inquest` rows across CSVs (e.g. linking `InquestDocument`/`Deceased` rows back to their `Inquest`) — treat it as an import-time join key, not a display field.

### Web layer

Search/detail pages are built on DRF generic views (`ListAPIView`, `RetrieveAPIView`) but render server-side HTML, not JSON: they set `renderer_classes = [TemplateHTMLRenderer]` and a `template_name`, so `Response(serializer.data)` becomes the template context directly (`{{ field_name }}` in the template, not `{{ data.field_name }}`).

Two shared mixins in `common/views.py` drive this:
- `KeywordSearchMixin` — adds free-text search (`?q=`, matched against a `search_fields` list via `icontains`), keyword multi-select filtering (`?keywords=<id>&keywords=<id>`), and column sorting (`?sort=<key>&dir=asc|desc`, driven by a `sort_fields` dict mapping a sort key to real queryset field(s)). It also injects the keyword options, current filter/sort state, and pre-built sort-toggle links (preserving other query params) into the response.
- `ActiveTabMixin` — injects `active_tab` on detail views so the sidebar can highlight the right section.

Templates: `common/templates/base.html` is the single shared shell (header, sidebar nav, and all page CSS as one embedded `<style>` block — there's no separate stylesheet or frontend build step). It's placed unnamespaced in `common/templates/` (rather than `common/templates/common/`) specifically so it resolves as a global `{% extends "base.html" %}` target from every app, unlike the app-specific templates which follow Django's normal namespaced convention (`inquests/templates/inquests/*.html`, `authorities/templates/authorities/*.html`). `base.html` defines `{% block sidebar %}` and `{% block content %}` (and a `{% block layout %}` wrapping both, which pages like the login form override to opt out of the sidebar entirely).

Routing (`project/urls.py`) has no root path — the app lives under `/inquests/`, `/inquests/<pk>/`, `/authorities/`, `/authorities/<pk>/`, plus `/accounts/login/`, `/accounts/logout/` (Django's built-in auth views), and `/admin/`.
