DOCKER_COMPOSE ?= docker-compose
DC_RUN_FLAGS=--rm

build:
	$(DOCKER_COMPOSE) build

test:
	$(DOCKER_COMPOSE) run antioch-tests
