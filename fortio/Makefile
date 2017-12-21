

deploy-fortio:
	istioctl kube-inject --debug=false -f fortio.yaml | kubectl apply -f -

# One time setup:
volume-setup:
	kubectl apply -f fortio-volume.yaml

.PHONY: deploy-fortio volume-setup
