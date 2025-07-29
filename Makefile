compose_api:
	docker network create unity-network > /dev/null 2>&1 || true
	docker compose -f ./docker-compose.local.yml up unity-auth-db unity-auth-api

compose_ui:
	docker network create unity-network > /dev/null 2>&1 || true
	docker compose -f ./docker-compose.local.yml up unity-auth-db unity-auth-ui

compose_all:
	docker network create unity-network > /dev/null 2>&1 || true
	docker compose -f ./docker-compose.local.yml up