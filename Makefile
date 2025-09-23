format:
	ruff format .
	ruff check --fix .
	isort .

clean:
	rm -rf build/ dist/ wheels/ *.egg-info
	find . -type d -name "__pycache__" -exec rm -rf {} +
	find . -type f -name "*.py[oc]" -delete
