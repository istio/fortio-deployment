Overview
====
This contains the Nginx configuration for istio.io and the associated subdomain
redirectors.

Testing
===
Configure kubectl to target a test cluster on GKE.

Run `make deploy-fake-secret deploy` and wait for the service to be available--
the load balancer may take some time to configure.

Set `TARGET_IP` to the ingress IP of the running service:

    export TARGET_IP=$(kubectl get svc istio-io '--template={{range .status.loadBalancer.ingress}}{{.ip}}{{end}}')

Use `make test` to run unit tests to verify the various endpoints on the server.

Deploying
===

Use canary.sh to verify configuration changes. This creates a seperate nginx deployment in the `istio-io-canary` namespace of the istio-io GKE cluster and runs some basic tests.

    ./canary.sh
    NAME       TYPE      DATA      AGE
    istio.io   Opaque    2         4h
    configmap "nginx" configured
    configmap "www-golang" configured
    deployment "istio-io" configured
    service "istio-io" configured
    deployment "istio-io" scaled
    deployment "istio-io" scaled
    waiting for all replicas to be up
    python test.py -q
    GET https://istio.io/manager/1720?go-get=1
    GET https://istio.io/mixer/1720?go-get=1
    REDIR: http://istio.io/manager?go-get=1 => https://istio.io/manager?go-get=1
    GET: https://istio.io/manager?go-get=1 => 200
    GET: https://istio.io => 200
    REDIR: http://istio.io => https://istio.io/
    REDIR: http://istio.io/4385 => https://istio.io/4385
    ----------------------------------------------------------------------
    Ran 3 tests in 0.710s
    
    OK

The canary cluster has a separate load balanced IP which can be used for additional manual checks. Use steps in the testing section above to determine the ingress IP.

For the real deployment set kubectl to target the production cluster and run `make deploy`. Nginx doesn't auto-detect configuration file changes so pods may need to be manually killed to force deployment to restart nginx with new configuration via ConfigMaps.
