build: .
	docker build -t taboo:latest .

shell: build
	docker run -v $(PWD):/app --rm -it --link postgres:postgres taboo:latest /bin/bash

lint: build
	docker run --rm taboo:latest black --check --diff /app

format: build
	docker run -v $(PWD):/app --rm taboo:latest black /app/

run: build
	docker-compose up

run-client: build
	docker run --rm --net=taboo_app -v $(PWD)/src/:/app/src/ taboo:latest python /app/src/client.py