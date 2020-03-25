build: .
	docker build -t taboo:latest .

shell: build
	docker run -v $(PWD):/app --rm -it --link postgres:postgres taboo:latest /bin/bash

lint: build
	docker run --rm taboo:latest black --check --diff /app

format: build
	docker run -v $(PWD):/app --rm taboo:latest black /app/

run: build
	docker run --rm -p 5000:5000 -e "FLASK_APP=src/app.py" --link postgres:postgres \
	taboo:latest flask run --port 5000 --host 0.0.0.0

db:
	docker run -e POSTGRES_PASSWORD=postgres -d -p 5400:5432 --name postgres postgres