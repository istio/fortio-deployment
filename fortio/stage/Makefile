
# TODO: parametrize the parent directory yaml etc instead of copy pasta
# on the other hand it is safer to not accidentally damage the prod version.


FORTIO_VERSION:=latest
FORTIO_IMAGE:=istio/fortio:$(FORTIO_VERSION)
FORTIO_MAX_STREAMS:=0

deploy-fortio:
	sed -e s%FORTIO_IMAGE%$(FORTIO_IMAGE)%g -e s%FORTIO_MAX_STREAMS%$(FORTIO_MAX_STREAMS)%g fortio.yaml | $(ISTIO_DIR)/bin/istioctl kube-inject --debug=false -f - | kubectl apply -f -

all: cert-setup ingress-setup cert-issue deploy-fortio

PROJECT:=istio-io
MACHINE_TYPE:=n1-standard-1
NUM_NODES:=3
EXTRA_CLUSTER_OPTIONS:=--no-enable-legacy-authorization --enable-autoupgrade --enable-autorepair --enable-autoscaling --min-nodes "3" --max-nodes "10"

create-cluster:
	gcloud container clusters create fortio-stage --zone us-west1-c --project $(PROJECT) --machine-type=$(MACHINE_TYPE) --num-nodes=$(NUM_NODES) $(EXTRA_CLUSTER_OPTIONS)

ISTIO_VERSION:=0.7.1
ISTIO_DIR:=istio-$(ISTIO_VERSION)
download-istio:
	curl -L https://git.io/getLatestIstio | ISTIO_VERSION=$(ISTIO_VERSION) sh -

install-istio:
	kubectl apply -f $(ISTIO_DIR)/install/kubernetes/istio-auth.yaml

cert-setup:
	# TODO: more granular rbac roles
	-kubectl create clusterrolebinding add-on-cluster-admin --clusterrole=cluster-admin --serviceaccount=kube-system:default
	helm init
	helm repo update
	sleep 5 # tiller not ready right away
	helm install stable/cert-manager

ingress-setup:
	kubectl apply -f ingress.yaml
	@echo "you now need to mark the ingress ip permanent, see kubectl get ingress"
	sleep 5 && kubectl get ingress
	@echo "also check the dns entry matches:"
	host fortio-stage.istio.io
	host istio-stage.fortio.org

cert-issue:
	kubectl apply -f cert.yaml

dump-images:
	kubectl get pods --all-namespaces -o jsonpath="{..image}" | \
		tr -s '[[:space:]]' '\n' | sort | uniq -c


#   dangerous as it deletes the cert and secret and if using the production
#   letsencrypt server, rate limits may mean you can't get a new cert until
#   the following week. uncomment if you understand the risks:
#force-reissue:
#	kubectl delete secret -n istio-system istio-ingress-certs

.PHONY: deploy-fortio cert-setup ingress-setup cert-issue all
