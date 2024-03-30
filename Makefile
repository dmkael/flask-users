start:
	flask --app main run --port 8000
start-debug:
	flask --app main --debug run --host=0.0.0.0 --port=8000
start-gunicorn:
	poetry run gunicorn --workers=4 --bind=127.0.0.1:8000 main:app
lint:
	poetry run flake8
