GIT_SHA ?= git-$(shell git rev-parse --short=12 HEAD)
DOCKER_REGISTRY ?= quay.io/theauthgear
APP_IMAGE_NAME ?= authgear-saml-sp-testing-tool
APP_IMAGE ?= $(DOCKER_REGISTRY)/$(APP_IMAGE_NAME):$(GIT_SHA)

.PYTHON_VERSION := 3.11

.PHONY: clean
clean:
	rm -rf ./venv

setup: venv

venv:
	python$(.PYTHON_VERSION) -m venv venv
	./venv/bin/pip install -r ./requirements.txt

.PHONY: start
start:
	FLASK_APP=app ./venv/bin/flask run --host=0.0.0.0 --port=5001 --debug

docker-run: image
	docker run --rm -p 5001:5001 ${APP_IMAGE}

.PHONY: image
image:
	docker build --platform linux/amd64 -t ${APP_IMAGE} .

.PHONY: push-image
push-image: image
	docker push ${APP_IMAGE}

.PHONY: compile-translations
compile-translations:
	source venv/bin/activate && pybabel compile -d translations

.PHONY: restart-app
restart-app: compile-translations
	pkill -f "flask run" || true
	FLASK_APP=app ./venv/bin/flask run --host=0.0.0.0 --port=5001 --debug &

.PHONY: update-translations
update-translations: compile-translations restart-app
