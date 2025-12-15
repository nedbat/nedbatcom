# Do everything for nedbatchelder.com

.DEFAULT_GOAL := help

##@ Deployment

.PHONY: publish stage live stoplive clean_cache
.PHONY: ned.% dep.% acc.% err.% ver.%

LIVEPORT = 8000

publish: ned.com 	## (ned.com) publish to nedbatchelder.com
stage: ned.net		## (ned.net) publish to nedbatchelder.net

env.%:
	op item get ned$*.env --fields label=text --format json | jq -r ".value" > deploy/.env

ned.%: env.% ## deploy to .net or .com
	DJANGO_SETTINGS_MODULE=djstell.settings_ned$*_base python djstell/bin/makehtml.py ned$* all
	rm deploy/.env
	rm to_dh/.env

dep.%: ## update dependencies for .net or .com
	scp -q requirements/server.txt dreamhost:nedbatchelder.$*/requirements
	ssh dreamhost venvs/ned$*/bin/python -m pip install -U pip
	ssh dreamhost venvs/ned$*/bin/python -m pip install -r nedbatchelder.$*/requirements/server.txt

acc.%: ## tail access logs for .net or .com
	ssh dreamhost tail -n100 -F logs/nedbatchelder.$*/https/access.log

err.%: ## show error logs for .net or .com
	ssh dreamhost tail -n100 -F djlog_ned$*.txt

ver.%: ## show versions running on .net or .com
	ssh dreamhost venvs/ned$*/bin/python -V
	ssh dreamhost venvs/ned$*/bin/python -m pip list | grep -i django

live: ## run a live dev Django server
	DJANGO_SETTINGS_MODULE=djstell.settings_live python djstell/bin/makehtml.py live clean load copy_verbatim support
	mkdir live/public/tabblo
	cp -R ../tabblo/[1-9]* live/public/tabblo
	python djstell/manage.py runserver --settings=djstell.settings_live

stoplive: ## stop the live dev Django server
	-kill $$(lsof -i tcp:$(LIVEPORT) | grep LISTEN | cut -f 2 -d ' ')

clean_cache: ## how to clean auto-made webp images
	@echo "To remove auto-made .webp images:"
	@echo "ssh dreamhost rm nedbatchelder.com/public/iv/webp/pix/etc"

showmemory: ## See memory use on dreamhost
	@echo '   PID %MEM %CPU VSZ'
	@ssh dreamhost "ps -eo pid,%mem,%cpu,vsz,command --sort=%mem | tail -20"
	@python -c 'import sys;print(round(sum(map(float, sys.argv[2:])),2))' $$(ssh dreamhost "ps -eo %mem")

showworkers: ## See systemctl on dreamhost
	 ssh dreamhost systemctl --user status

##@ Maintenance

.PHONY: upgrade backupcomments db.%

PIPCOMPILE = pip-compile --upgrade --rebuild --resolver=backtracking

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

db.%: env.% ## connect to the database for .net or .com
	set -o allexport; . deploy/.env; set +o allexport; mycli -h mysql2.nedbatchelder.net -u ned$*_reactor -p "$$REACTOR_PASSWORD" ned$*_reactor
	rm deploy/.env

livedb: ## open phpMyAdmin for nedbatchelder.com
	@echo https://panel.dreamhost.com/index.cgi?tree=advanced.mysql
	@echo https://east1-phpmyadmin.dreamhost.com/signon.php?pma_servername=guelff.iad1-mysql-e2-15a.dreamhost.com

##@ Testing

.PHONY: install loadlivecomments html test linkcheck livelinkcheck

install: ## install the local dev requirements
	python -m pip install -r requirements/dev.txt
	playwright install

loadlivecomments: ## load latest comments into live server
	sqlite3 djstell/reactor.db 'delete from reactor_comment'
	django-admin loaddata --settings=djstell.settings_live --database=reactor $$(ls -1 data/*.json | tail -1)

WGET_OPTS = \
	--no-verbose \
	--directory-prefix=html \
	--no-host-directories \
	--adjust-extension \
	--retry-connrefused \
	--max-redirect=3 \
	--recursive \
	--level=inf \
	--execute robots=off

LIVEHOST = http://127.0.0.1:$(LIVEPORT)
HTML_URLS = \
	$(LIVEHOST) \
	$(LIVEHOST)/blog/drafts.html \
	$(LIVEHOST)/err404.html \
	$(LIVEHOST)/summary.json

html: stoplive	 ## make HTML for comparing and examining
	LIVE_NODJTB=1 REPEATABLE=1 make live &
	sleep 20
	wget $(WGET_OPTS) $(HTML_URLS)

test: ## run the few tests we have
	@echo 'run `make live` first to run the server to test against'
	DJANGO_SETTINGS_MODULE=djstell.settings_live pytest --base-url http://127.0.0.1:8000 -vv djstell

linkcheck: ## check the links on nedbatchelder.com
	linkchecker -f etc/linkcheckerrc https://nedbatchelder.com

livelinkcheck: ## check the links on the live local server
	linkchecker -t 12 -f etc/linkcheckerrc http://127.0.0.1:8000

##@ Clean up

.PHONY: clean sterile

clean: ## get rid of stuff we don't need
	rm -rf html live to_dh local
	rm -f deploy/.env

sterile: clean ## extra-clean
	rm -rf html0

##@ Helpful

.PHONY: help

help: ## display this help message
	@# Adapted from https://www.thapaliya.com/en/writings/well-documented-makefiles/
	@echo Available targets:
	@awk 'BEGIN{FS=":.*##";} /^[^: ]+:.*##/{printf "\033[1m %-15s\033[m %s\n",$$1,$$2} /^##@/{printf "\n%s:\n",substr($$0,5)}' $(MAKEFILE_LIST)
