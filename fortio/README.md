# Fortio on Istio

Experimental istio on istio deployment:

[https://fortio.istio.io/](https://fortio.istio.io/) is running an istio deployment of the `fortio report` application used to serve performance results.

Using envoy directly as the internet facing istio ingress. SSL certificates are
automatically provisioned and renewed for multiple domains
([https://istio.fortio.org/](https://istio.fortio.org/) being the second one for the sake of this demonstration).

The data presented is pulled from a configurable google cloud storage or aws s3 bucket.

Before making any change here, you must try the changes in [stage/](stage/) first.

## Initial setup:

One time setup:

- 3 Nodes 1 vCPU elastic cluster `istio-prod` (can be redone for `istio-stage` but must stay permanently including upgrades to be tested on stage first, for the prod one)

- Istio itself
  ```
  # Istio 'perf' mode installation:
  sh -c 'sed -e "s/_debug//g" install/kubernetes/istio-auth.yaml | egrep -v -e "- (-v|\"2\")" | kubectl apply -f -'
  ```

- Cert-manager

  This installs the [cert-manager](https://github.com/jetstack/cert-manager)
  ```
  make cert-setup
  ```

- Ingress

  You can run this step separately for instance if you change ingress rules
  in ingress.yaml.
  ```
  make ingress-setup
  ```

- Get SSL certs

  You can run this step separately for instance if switching from staging to
  prod or editing cert.yaml to add new domains for instance.

  The ingress ip and DNS must match.

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
