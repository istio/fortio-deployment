# Fortio on Istio

Experimental istio on istio deployment:

fortio.istio.io is running an istio deployment of the `fortio report` application

Using envoy directly as the internet facing istio ingress. SSL certificates are
automatically provisioned and renewed.

The data presented is pulled from a configurable google cloud storage or aws s3 bucket.

## Initial setup:

One time setup:

- Istio itself
```
# Istio 'perf' mode installation:
sh -c 'sed -e "s/_debug//g" install/kubernetes/istio-auth.yaml | egrep -v -e "- (-v|\"2\")" | kubectl apply -f -'
```

- cert-manager
```
make cert-setup
```
- ingress
```
make ingress-setup
```
- Get SSL certs
you can run this step separately for instance if adding new domains to cert.yaml
```
make cert-issue
```
(check pod logs at each step etc)

## Fortio report app

Install fortio report app:
```
make deploy-fortio # or just 'make'
```

You can also delete the fortio-report pods to upgrade to latest fortio
