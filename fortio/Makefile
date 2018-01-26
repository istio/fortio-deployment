
deploy-fortio:
	istioctl kube-inject --debug=false -f fortio.yaml | kubectl apply -f -

all: cert-setup ingress-setup cert-issue deploy-fortio

cert-setup:
	# TODO: more granular rbac roles
	-kubectl create clusterrolebinding add-on-cluster-admin --clusterrole=cluster-admin --serviceaccount=kube-system:default
	helm init
	helm repo update
	helm install stable/cert-manager

ingress-setup:
	kubectl apply -f ingress.yaml

cert-issue:
	kubectl apply -f cert.yaml

#   dangerous as it deletes the cert and secret and if using the production
#   letsencrypt server, rate limits may mean you can't get a new cert until
#   the following week. uncomment if you understand the risks:
#force-reissue:
#	kubectl delete secret -n istio-system istio-ingress-certs

.PHONY: deploy-fortio cert-setup ingress-setup cert-issue all
