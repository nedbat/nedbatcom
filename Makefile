.PHONY: help publish html css js live local test clean

.DEFAULT_GOAL := help

help: ## display this help message
	@echo "Please use \`make <target>' where <target> is one of"
	@awk -F ':.*?## ' '/^[a-zA-Z]/ && NF==2 {printf "\033[36m  %-25s\033[0m %s\n", $$1, $$2}' $(MAKEFILE_LIST) | sort

publish: ## publish to Webfaction
	DJANGO_SETTINGS_MODULE=djstell.settings_webfaction python djstell/bin/makehtml.py wf all

html: ## make HTML for uploading
	DJANGO_SETTINGS_MODULE=djstell.settings_webfaction python djstell/bin/makehtml.py wf clean load make

css: ## make css from .scss
	for f in style/[a-z]*.scss; do \
		pysassc --style=compressed $$f static/$$(basename $${f%.scss}.css); \
	done

js: static/nedbatchelder.js
static/nedbatchelder.js:
	echo "" >$@
	for f in $$(<js/ingredients.txt); do \
		cat js/$$f >>$@; \
		echo "" >>$@; \
	done

live: ## run a live dev Django server
	DJANGO_SETTINGS_MODULE=djstell.settings_live python djstell/bin/makehtml.py live clean load copy_verbatim support
	python djstell/manage.py runserver --settings=djstell.settings_live

local: ## run a local Django server
	DJANGO_SETTINGS_MODULE=djstell.settings_local python djstell/bin/makehtml.py local clean load copy_verbatim support djstell copy_live
	cd local; PYTHONPATH=/Users/nedbatchelder/py:. python djstell/manage.py runserver --settings=djstell.settings_local

nednet:
	DJANGO_SETTINGS_MODULE=djstell.settings_nednet_base python djstell/bin/makehtml.py nednet all

nedcom:
	DJANGO_SETTINGS_MODULE=djstell.settings_nedcom_base python djstell/bin/makehtml.py nedcom all

nedwiz:
	DJANGO_SETTINGS_MODULE=djstell.settings_nedwiz_base python djstell/bin/makehtml.py nedwiz all

test: ## run the few tests we have
	DJANGO_SETTINGS_MODULE=djstell.settings_live pytest --base-url http://127.0.0.1:8000 djstell

clean: ## get rid of stuff we don't need
	rm -rf html live

sterile: clean ## extra-clean
	rm -rf html0
