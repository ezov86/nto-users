.PHONY: build run down stop test

CONTAINER=nto-users

build:
	docker build . -t $(CONTAINER)

run:
	docker compose up -d

stop:
	docker compose stop

down:
	docker compose down

test:
	docker exec $(CONTAINER) sh -c "cd app; coverage run -m pytest tests/; coverage report"
