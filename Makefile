build: .
	docker build -t taboo:latest .

shell: build
	docker run --rm -it taboo:latest /bin/bash

lint: build
	docker run --rm taboo:latest black --check --diff

format: build
	docker run -v $PWD:/app --rm taboo:latest black
