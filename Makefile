all: 
	@python3 app.py

install:
	@echo "installing dependencies"
	@sudo apt-get update
	@sudo apt-get install -y python3 pip 
	@pip install flask watchdog jinja2 markdown
	@echo "Dependencies installed successfully."

