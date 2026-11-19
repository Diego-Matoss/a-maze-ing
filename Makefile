PYTHON      = python3
PIP         = pip
MAIN        = a_maze_ing.py
CONFIG      = config.txt
TARGETS     = $(MAIN) mazegen maze_app

MYPY_FLAGS  = --warn-return-any --warn-unused-ignores \
              --ignore-missing-imports --disallow-untyped-defs \
              --check-untyped-defs

.PHONY: install run debug clean lint lint-strict

install:
	$(PIP) install -r requirements-dev.txt

run:
	$(PYTHON) $(MAIN) $(CONFIG)

debug:
	$(PYTHON) -m pdb $(MAIN) $(CONFIG)

clean:
	find . -type d -name "__pycache__" -exec rm -rf {} +
	rm -rf .mypy_cache .pytest_cache build dist *.egg-info

lint:
	flake8 $(TARGETS)
	mypy $(MYPY_FLAGS) $(TARGETS)

lint-strict:
	flake8 $(TARGETS)
	mypy --strict $(TARGETS)
