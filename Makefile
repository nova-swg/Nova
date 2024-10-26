all: 
	@python3 app.py

install:
	@echo "installing dependencies"
	@sudo apt-get update
	@sudo apt-get install -y python3 pip 
	@pip install flask watchdog jinja2 markdown uwsgi
	@echo "Dependencies installed successfully."

prod:
	@uwsgi --http 127.0.0.1:8000 --master -p 4 -w app:app