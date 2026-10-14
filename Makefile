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

debug:
	python3 -m pdb pac-man.py config.json

pkg:
	python3 -m PyInstaller --clean 42-Pac-Man.spec

clean:
		rm -rf build
		rm -rf maze.txt
		rm -rf dist
		rm -rf __pycache__
		rm -rf .mypy_cache
