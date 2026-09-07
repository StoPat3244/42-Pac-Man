MAZEGEN = ./mazegen/mazegenerator-2.1.0-py3-none-any.whl

all: run

install:
		pip install pygame
		pip install flake8
		pip install mypy
		pip install $(MAZEGEN)

lint:
		python3 -m flake8
		mypy . --warn-return-any --warn-unused-ignores --ignore-missing-imports --disallow-untyped-defs	--check-untyped-defs

run:
	python3 main.py config.json


clean:
		rm -rf test.txt