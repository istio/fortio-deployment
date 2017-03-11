#!/bin/bash

set -o errexit
set -o nounset
set -o pipefail

function kc() {
  kubectl --context=utilicluster --namespace=istio-io-canary "$@"
}

kc apply \
    -f configmap-nginx.yaml \
    -f configmap-www-get.yaml \
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

make test TARGET_IP=104.197.208.221
