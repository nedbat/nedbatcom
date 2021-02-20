.PHONY: help publish test

.DEFAULT_GOAL := help

help: ## display this help message
	@echo "Please use \`make <target>' where <target> is one of"
	@awk -F ':.*?## ' '/^[a-zA-Z]/ && NF==2 {printf "\033[36m  %-25s\033[0m %s\n", $$1, $$2}' $(MAKEFILE_LIST) | sort

publish: ## publish to Webfaction
	python djstell/bin/makehtml.py wf all

test: ## run the few tests we have
	pytest djstell/pages/tests.py
