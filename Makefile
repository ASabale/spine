.PHONY: test lint typecheck invariants coverage build smoke release

UV ?= uv
PYTEST ?= $(UV) run pytest
PYTHON ?= $(UV) run python

test:
	$(PYTEST) -q

invariants:
	$(PYTEST) -q tests/test_invariants.py tests/test_harness.py tests/test_claims.py tests/test_security.py tests/test_migrate.py

lint:
	$(PYTHON) -m compileall -q src/spine

typecheck:
	$(PYTHON) -c "from spine.cli import main; from spine.engine import advance; from spine.migrate import migrate; from spine.store import CoordStore"

coverage:
	$(PYTEST) -q --cov=spine --cov-fail-under=70

build:
	$(UV) build

smoke:
	$(UV) run spine --help
	$(UV) run spine --version

release: lint typecheck test invariants coverage build smoke
	@echo "release ok"
