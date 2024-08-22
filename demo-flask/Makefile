GIT_SHA ?= git-$(shell git rev-parse --short=8 HEAD)
DOCKER_REGISTRY ?= us-east1-docker.pkg.dev/oursky-kube/pandawork
APP_IMAGE_NAME ?= authgear-demo-saml-sp
APP_IMAGE ?= $(DOCKER_REGISTRY)/$(APP_IMAGE_NAME):$(GIT_SHA)


.PHONY: start
start:
	FLASK_APP=app pipenv run flask run --host=0.0.0.0 --port=5001

.PHONY: image
image:
	docker build --platform linux/amd64 -t ${APP_IMAGE} .

.PHONY: push-image
push-image: image
	docker push ${APP_IMAGE}
