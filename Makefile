.PHONY: help publish html css js live test clean

.DEFAULT_GOAL := help

help: ## display this help message
	@echo "Please use \`make <target>' where <target> is one of"
	@awk -F ':.*?## ' '/^[a-zA-Z]/ && NF==2 {printf "\033[36m  %-25s\033[0m %s\n", $$1, $$2}' $(MAKEFILE_LIST) | sort

publish: ## publish to Webfaction
	python djstell/bin/makehtml.py wf all

html: ## make HTML for uploading
	python djstell/bin/makehtml.py wf clean load make

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

live: ## run a local Django server
	python djstell/bin/makehtml.py live clean load copy_verbatim copy_db support
	python djstell/manage.py runserver --settings=djstell.settings_live

nednet:
	python djstell/bin/makehtml.py nednet clean load copy_verbatim copy_db support rsync

test: ## run the few tests we have
	pytest djstell/pages/tests.py

clean: ## get rid of stuff we don't need
	rm -rf html html0
