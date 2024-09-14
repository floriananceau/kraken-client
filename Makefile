install:
	uv sync

check:
	uv run ruff check src/

format:
	uv run ruff format src/

tests:
	uv run pytest --cov=kraken_client src/

build:
	uv build

publish:
	TWINE_PASSWORD=${CI_JOB_TOKEN} TWINE_USERNAME=gitlab-ci-token uvx twine upload --repository-url ${CI_API_V4_URL}/projects/${CI_PROJECT_ID}/packages/pypi dist/*

docs:
	uv run sphinx-build -b html docs/source/ public/