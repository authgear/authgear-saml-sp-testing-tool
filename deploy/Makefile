GIT_SHA ?= git-$(shell git rev-parse --short=8 HEAD)
K8S_NAMESPACE ?= authgear-demo

.PHONY: deploy
deploy:
	helm upgrade authgear-demo-saml-sp ./helm --install \
		--wait --wait-for-jobs --cleanup-on-fail \
		-n $(K8S_NAMESPACE) \
		--set-string appVersion="$(GIT_SHA)"
