
deploy-fortio:
	istioctl kube-inject --debug=false -f fortio.yaml | kubectl apply -f -

cert-setup:
	# TODO: more granular rbac roles
	-kubectl create clusterrolebinding add-on-cluster-admin --clusterrole=cluster-admin --serviceaccount=kube-system:default
	helm init
	helm install --name cert-manager cert-manager/contrib/charts/cert-manager/

ingress-setup:
	kubectl apply -f ingress.yaml

cert-issue:
	kubectl apply -f cert.yaml

# dangerous
#force-reissue:
#	kubectl delete secret -n istio-system istio-ingress-certs

.PHONY: deploy-fortio volume-setup cert-setup ingress-setup cert-issue
