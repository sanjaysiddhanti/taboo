build: .
	docker build -t taboo:latest .

shell: build
	docker run --rm -it taboo:latest /bin/bash

lint: build
	docker run --rm taboo:latest black --check --diff

format: build
	docker run -v $PWD:/app --rm taboo:latest black

run: build
	docker run --rm -p 5000:5000 -e "FLASK_APP=src/app.py" \
	taboo:latest flask run --port 5000 --host 0.0.0.0