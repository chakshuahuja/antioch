DOCKER_COMPOSE ?= docker-compose
DC_RUN_FLAGS=--rm

build:
	$(DOCKER_COMPOSE) build

test:
	$(DOCKER_COMPOSE) run antioch-tests

generate_dev_assertion_certs:
	openssl req -x509 -nodes -newkey rsa:2048 -keyout saml_sign_cert.key -out saml_sign_cert.crt