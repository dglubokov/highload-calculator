init: dockerinit updatedeps

dockerinit:
	docker-compose build
	docker-compose create

updatedeps:
	pipenv install

updatedevdeps:
	pipenv install --dev

run:
	pipenv run python ./calculator/main.py

runisolated:
	docker-compose up -d

