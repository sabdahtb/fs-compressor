CURRENT_DIR?=$(patsubst %/,%,$(dir $(realpath $(firstword $(MAKEFILE_LIST)))))
ROOT_DIR?=$(CURRENT_DIR)
DOCKER_COMPOSE?=docker-compose

build:
	$(DOCKER_COMPOSE) up --build --no-recreate -d

up:
	$(DOCKER_COMPOSE) up -d

check:
	$(DOCKER_COMPOSE) ps

kill:
	$(DOCKER_COMPOSE) kill || true
	$(DOCKER_COMPOSE) rm --force || true

run: build check up