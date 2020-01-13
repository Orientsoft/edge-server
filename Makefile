.PHONY: build push

DEPLOY_NAMESPACE = default
TAG             = $(shell git describe --tags --always)
REGISTRY        = registry.mooplab.com:8443/kubeedge
IMAGE           = edge-server


build:
	docker build --network host --rm -t "$(REGISTRY)/$(IMAGE):$(TAG)" -f Dockerfile .
