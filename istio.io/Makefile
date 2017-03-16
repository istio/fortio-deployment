all: test

.PHONY: deploy-fake-secret
deploy-fake-secret:
	openssl genrsa -out tls.key 2048
	openssl req -new -key tls.key -out tls.csr -subj '/CN=istio.io/O=TEST/C=US'
	openssl x509 -req -days 10000 -in tls.csr -signkey tls.key -out tls.crt
	kubectl get istio.io || kubectl create secret generic istio.io --from-file=tls.key=tls.key --from-file=tls.crt=tls.crt

.PHONY: deploy
deploy:
	kubectl get secret/ssl || kubectl apply -f secret-ssl.yaml
	kubectl apply -f configmap-nginx.yaml
	kubectl apply -f configmap-www-golang.yaml
	kubectl apply -f service-prod.yaml
	kubectl apply -f deployment.yaml

.PHONY: test
test:
	python test.py -q

.PHONY: docker-test
docker-test:
	docker build -t istio-io-test -f Dockerfile-test .
	docker run -it --rm -e TARGET_IP=${TARGET_IP} istio-io-test
