#!/bin/bash

set -o errexit
set -o nounset
set -o pipefail

function kc() {
  kubectl --context=gke_istio-io_us-west1-b_istio-io-cluster --namespace=istio-io-canary "$@"
}

function create_secret() {
    openssl genrsa -out tls.key 2048
    openssl req -new -key tls.key -out tls.csr -subj '/CN=istio.io/O=TEST/C=US'
    openssl x509 -req -days 10000 -in tls.csr -signkey tls.key -out tls.crt
    kc create secret generic istio.io --from-file=tls.key=tls.key --from-file=tls.crt=tls.crt
}

kc get secret/istio.io || create_secret

kc apply \
    -f configmap-nginx.yaml \
    -f configmap-www-golang.yaml \
    -f deployment.yaml \
    -f service-canary.yaml

kc scale deployment istio-io --replicas=0
kc scale deployment istio-io --replicas=1

while true; do
  echo "waiting for all replicas to be up"
  sleep 3
  read WANT HAVE < <( \
      kc get deployment istio-io \
          -o go-template='{{.spec.replicas}} {{.status.replicas}}{{"\n"}}'
  )
  if [ -n "${WANT}" -a -n "${HAVE}" -a "${WANT}" == "${HAVE}" ]; then
    break
  fi
  echo "want ${WANT}, found ${HAVE}"
done

make test TARGET_IP=104.198.5.229
