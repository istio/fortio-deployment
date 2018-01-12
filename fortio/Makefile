
deploy-fortio:
	istioctl kube-inject --debug=false -f fortio.yaml | kubectl apply -f -

# One time setup:
volume-setup:
	kubectl apply -f fortio-volume.yaml

cert-setup:
	# TODO: more granular rbac roles
	-kubectl create clusterrolebinding add-on-cluster-admin --clusterrole=cluster-admin --serviceaccount=kube-system:default
	helm init
	helm install --name cert-manager cert-manager/contrib/charts/cert-manager/

ingress-setup:
	kubectl apply -f ingress.yaml

cert-issue:
	kubectl apply -f cert.yaml

# TODO: find a way to avoid this (but needed for now because of auth)
# E0112 03:02:54.090362       1 prepare.go:158] Error cleaning up solver: [istio.fortio.org] Error cleaning up ingress: error cleaning up ingress: Ingress.extensions "cert-manager-temp-ingress" is invalid: spec.rules[0].http.paths: Required value
cleanup:
	kubectl delete ingress -n istio-system cert-manager-temp-ingress

.PHONY: deploy-fortio volume-setup cert-setup
