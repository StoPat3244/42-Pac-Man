MAZEGEN = ./assets/mazegenerator-2.1.0-py3-none-any.whl

all: install run

install:
		pip install pygame-ce
		pip install flake8
		pip install mypy
		pip install $(MAZEGEN)

lint:
		python3 -m flake8
		mypy . --warn-return-any --warn-unused-ignores --ignore-missing-imports --disallow-untyped-defs	--check-untyped-defs

run:
	python3 pac-man.py config.json


clean:
		rm -rf test.txt
