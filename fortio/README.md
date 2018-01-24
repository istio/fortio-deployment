# Fortio on Istio

Experimental istio on istio deployment:

fortio.istio.io is running an istio deployment of the `fortio report` application

Using envoy directly as the internet facing istio ingress.

The data presented is pulled from a configurable google cloud storage or aws s3 bucket.

Intial setup:
```
# Istio 'perf' mode installation:
sh -c 'sed -e "s/_debug//g" install/kubernetes/istio-auth.yaml | egrep -v -e "- (-v|\"2\")" | kubectl apply -f -'
```

Install fortio report app:
```
make deploy-fortio
```
