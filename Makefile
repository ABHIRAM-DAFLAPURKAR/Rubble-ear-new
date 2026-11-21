.PHONY: setup test test-py test-web typecheck lint golden synth-train build dev icons
setup:
	python3 -m pip install -r ml/requirements.txt && cd web && npm install
test: test-py test-web
test-py:
	cd ml && python3 -m pytest -q
test-web:
	cd web && npx vitest run
typecheck:
	cd web && npx tsc --noEmit
lint:
	ruff check ml
golden:
	python3 ml/scripts/make_golden.py
synth-train:
	cd ml && PYTHONPATH=src python3 -m rubble_ear.train denoiser --smoke && PYTHONPATH=src python3 -m rubble_ear.train classifier --smoke && PYTHONPATH=src python3 -m rubble_ear.train range --smoke
build:
	cd web && npm run build
dev:
	cd web && npm run dev
icons:
	python3 scripts/make_icons.py
