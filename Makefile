.PHONY: help install up reset test clean

help: ## Mostrar ayuda
	@echo "Comandos disponibles:"
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | sort | awk 'BEGIN {FS = ":.*?## "}; {printf "\033[36m%-20s\033[0m %s\n", $$1, $$2}'

install: ## Instalar dependencias con Poetry
	poetry install

up: ## Levantar el sistema
	@echo "🚀 Levantando sistema de agentes AI..."
	@echo "✅ Sistema listo para usar"
	@echo "🎯 Ejemplo: python -m agentesai.cli '¿quién soy?'"

reset: ## Reset del sistema a estado original
	@echo "🔄 Reseteando sistema..."
	poetry run python -m agentesai.cli --reset

test: ## Ejecutar tests
	@echo "🧪 Ejecutando tests..."
	poetry run pytest

clean: ## Limpiar archivos generados
	@echo "🧹 Limpiando archivos..."
	find . -type f -name "*.pyc" -delete
	find . -type d -name "__pycache__" -delete
	rm -rf .pytest_cache
	rm -rf build/
	rm -rf dist/ 