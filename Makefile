.PHONY: help publish stage html css js

.DEFAULT_GOAL := help

##@ Deployment

.PHONY: publish stage ned.% dep.% live local

publish: ned.com 	## (ned.com) publish to nedbatchelder.com
stage: ned.net		## (ned.net) publish to nedbatchelder.net

ned.%: ## deploy to nedbatchelder.net or .com
	DJANGO_SETTINGS_MODULE=djstell.settings_ned$*_base python djstell/bin/makehtml.py ned$* all

dep.%: ## update dependencies for nedbatchelder.net or .com
	scp -q requirements/server.txt dreamhost:nedbatchelder.$*/requirements
	ssh dreamhost venvs/ned$*/bin/python -m pip install -r nedbatchelder.$*/requirements/server.txt

live: ## run a live dev Django server
	DJANGO_SETTINGS_MODULE=djstell.settings_live python djstell/bin/makehtml.py live clean load copy_verbatim support
	python djstell/manage.py runserver --settings=djstell.settings_live

local: ## run a local Django server
	DJANGO_SETTINGS_MODULE=djstell.settings_local python djstell/bin/makehtml.py local clean load copy_verbatim support djstell copy_live
	cd local; PYTHONPATH=/Users/nedbatchelder/py:. python djstell/manage.py runserver --settings=djstell.settings_local

##@ Maintenance

PIPCOMPILE = pip-compile -v --upgrade --rebuild --annotation-style=line

upgrade: export CUSTOM_COMPILE_COMMAND=make upgrade
upgrade: ## update the pip requirements files to use the latest releases satisfying our constraints
	pip install -qr requirements/pip-tools.txt
	# Make sure to compile files after any other files they include!
	$(PIPCOMPILE) -o requirements/pip-tools.txt requirements/pip-tools.in
	$(PIPCOMPILE) -o requirements/base.txt requirements/base.in
	$(PIPCOMPILE) -o requirements/dev.txt requirements/dev.in
	$(PIPCOMPILE) -o requirements/server.txt requirements/server.in

backupcomments: ## get a backup of the live comments on nedbatchelder.com
	django-admin dumpdata --settings=djstell.settings_nedcom_db -o data/reactor_$$(date +%Y%m%d).json --database=reactor reactor.Comment

##@ Testing

.PHONY: html css js test linkcheck

loadlivecomments: ## load latest comments into live server
	sqlite3 djstell/reactor.db 'delete from reactor_comment'
	django-admin loaddata --settings=djstell.settings_live --database=reactor $$(ls -1 data/*.json | tail -1)

html: ## make HTML for comparing and examining
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

test: ## run the few tests we have
	DJANGO_SETTINGS_MODULE=djstell.settings_live pytest --base-url http://127.0.0.1:8000 djstell

linkcheck: ## check the links on nedbatchelder.com
	linkchecker -f etc/linkcheckerrc https://nedbatchelder.com

livelinkcheck: ## check the links on the live local server
	linkchecker -t 12 -f etc/linkcheckerrc http://127.0.0.1:8000

##@ Clean up

.PHONY: clean sterile

clean: ## get rid of stuff we don't need
	rm -rf html live to_dh local

sterile: clean ## extra-clean
	rm -rf html0

##@ Helpful

.PHONY: help

help: ## display this help message
	@# Adapted from https://www.thapaliya.com/en/writings/well-documented-makefiles/
	@echo Available targets:
	@awk 'BEGIN {FS = ":.*##";} /^[^: ]+:.*?##/ { printf "\033[1m  %-15s\033[0m %s\n", $$1, $$2 } /^##@/ { printf "\n%s:\n", substr($$0, 5) }' $(MAKEFILE_LIST)
