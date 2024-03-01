SHELL := /bin/bash

all: venv
	. .env/Scripts/activate && $(MAKE) build

build: venv
	python build.py

venv: .env/touchfile

.env/touchfile: requirements.txt
	test -d .env || py -m venv .env
	dos2unix .env/Scripts/activate
	. .env/Scripts/activate && pip install -r requirements.txt
	touch .env/touchfile

clean:
	/usr/bin/find . -name '__pycache__' | xargs --no-run-if-empty rm -r
	-rm -rf build dist

clean-env:
	-rm -rf .env

purge: clean clean-env
