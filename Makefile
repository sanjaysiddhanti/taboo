build: .
	docker build -t taboo:latest .

shell: build
	docker run -v $(PWD):/app --rm -it --net taboo_app taboo:latest /bin/bash

lint: build
	docker run --rm taboo:latest black --check --diff /app

format: build
	docker run -v $(PWD):/app --rm taboo:latest black /app/

run: build
	docker-compose up

build-static-assets: build
	docker run --rm -v $(PWD):/app taboo:latest npm run build

deploy-frontend-to-s3: build build-static-assets
	aws s3 sync build/ s3://taboo-deploy