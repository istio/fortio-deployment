
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

.PHONY: deploy-fortio volume-setup cert-setup
