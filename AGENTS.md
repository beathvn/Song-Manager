# Repository Guidelines

## Project Structure & Module Organization

Song-Manager is a Python 3.11+ `uv` workspace for managing Spotify and Rekordbox music libraries. Runnable workflows live in `services/<service>/`: Python entry points are in `src/`, shell launchers in `scripts/`, example settings in `env/.env.example` or `config/`, and exploratory notebooks in `research/`. Shared packages are workspace members under `libs/` (`spotify_client`, `rekordbox_client`, and `song_common`). User-facing notes live in `README.md` and `docs/`.

Keep service-specific behavior inside its service; add reusable Spotify, Rekordbox, or logging code to the appropriate library package.

## Documentation Synchronization

`docs/00 Overview.md` is the concise source of truth for the project’s
high-level workflows, responsible services, and implementation status. When a
code change alters a service’s behavior, workflow, inputs, outputs, ownership,
or readiness, update that overview in the same change so the architecture
documentation and code do not drift apart. Keep it concise; service READMEs
remain the place for command-specific setup and troubleshooting.

Write Markdown prose as one physical line per paragraph. Use a blank line when starting a distinct topic or Markdown block; do not add soft line breaks solely to wrap text.

## Build, Test, and Development Commands

- On macOS, activate the project environment with `source .venv/bin/activate`
  before running Ruff or Python commands.
- `uv sync` creates the project virtual environment and installs locked dependencies.
- `pre-commit install` enables the repository hooks locally; `pre-commit run --all-files` runs them on demand.
- `uv run ruff check .` reports lint issues, and `uv run ruff format --check .` verifies formatting.
- Run a workflow through its launcher after configuring its environment, e.g. `./services/spotify_discovery/scripts/create_new_arrivals.sh`.

Install `ffmpeg` on macOS (`brew install ffmpeg`) before using audio-normalization features. Make newly added shell launchers executable with `chmod +x path/to/script.sh`.

## Coding Style & Naming Conventions

Use four-space indentation, double quotes, and an 88-character line limit, matching the Ruff configuration in `pyproject.toml`. Use `snake_case` for modules, functions, variables, and scripts; use kebab-case for public CLI flags; use `PascalCase` for classes and Pydantic models. Add type annotations to new Python functions and keep imports grouped as standard library, third-party, then internal packages. Prefer explicit CLI arguments and logging over hard-coded machine-specific paths or `print` statements.

### Engineering Guidelines

- Use the fewest precise words in human-facing text, including comments, commit messages, and replies. Avoid superlatives and praise.
- Extract recurring, meaningful, or specification-defined values into descriptive constants or enums. Keep self-explanatory one-off values inline.
- Prefer early returns and `continue` statements to reduce indentation. Keep function names under 30 characters.
- Use enums, not booleans, for function parameters when a named state improves clarity.
- Separate logical code blocks with blank lines. Add brief comments only for blocks created or modified, explaining what and why; use examples where helpful. Propose ASCII diagrams for complete systems.
- Treat visibility changes as breaking design changes. Keep fields and functions private unless the design requires otherwise, and obtain explicit approval before changing private members to internal or public.
- Encapsulate low-level mechanics in dedicated driver or abstraction layers. Expose high-level domain APIs to callers.
- Respect adjacent-layer boundaries: a layer may call only its immediate layer below. Route UI or controller access to data stores, drivers, and low-level clients through intermediate services or abstractions.
- Change only code related to the requested feature and minimize modified lines.
- Finder launchers must not require command-line arguments. They may load a fixed ignored environment file from their own `env/` directory; the service README must name it and its tracked example, if any.

## Testing Guidelines

There is currently no dedicated automated test suite. For changes, at minimum run Ruff and exercise the affected command with a safe copy of the XML, playlist, or media data. Add focused `pytest` tests under a new `tests/` directory when introducing logic that can be tested without Spotify credentials or local Rekordbox data; name them `test_<behavior>.py`.

When fixing a bug, write a focused failing test first, observe it fail, then implement the fix and observe the test pass.

## Commit & Pull Request Guidelines

Use a capitalized, imperative subject of 50 characters or fewer (72 absolute maximum), without a period. Separate it from an optional body with one blank line. Manually wrap body lines at 72 characters; explain what and why, not how. Keep commits focused and describe the affected service when useful. Pull requests should explain the behavior change, list validation performed, link related issues, and include screenshots or sample output for user-visible or data-format changes. Never commit `.env.local`, OAuth credentials, absolute library locations, or personal music/XML exports; update the relevant `.env.example` or example config instead.
