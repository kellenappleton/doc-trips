

VENV=venv
PYTHON=$(VENV)/bin/python
PIP=$(VENV)/bin/pip
FAB=$(VENV)/bin/fab
COVERAGE=$(VENV)/bin/coverage

MANAGE=$(PYTHON) doc-trips/manage.py

BEHAVE=$(VENV)/bin/behave
FEATURES=doc-trips/features/

.PHONY: install migrations migrate behave behave_dry rm_emacs_locks test coverage clean deploy

all:
	$(MANAGE) runserver

install:
	pyvenv $(VENV)
	$(PIP) install -r requirements.txt

deploy: 
	heroku maintenance:on
	git push heroku master
	heroku run migrate
	heroku maintenance:off

migrations:
	$(MANAGE) makemigrations

migrate:
	$(MANAGE) migrate

superuser:
	$(MANAGE) setsuperuser d34898x

test: 
	$(MANAGE) test doc-trips

coverage:
	$(COVERAGE) run --omit "$(VENV)/*" $(MANAGE) test
	$(COVERAGE) report -m
	$(COVERAGE) html -d coverage

clean: 
	rm -rf *.pyc
	rm -rf *~
