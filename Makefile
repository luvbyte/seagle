.PHONY: venv install run


# PYPATH = $(HOME)/myenv/bin/python3
PYPATH = ../venv/bin/python3

venv:
	python3 -m venv venv

# Install dependencies from requirements.txt
install:
	venv/bin/python3 -m pip install -r requirements.txt
	@echo "Dependencies installed."

test:
	cd seagle && $(PYPATH) test.py

run:
	cd seagle && $(PYPATH) main.py
