SHELL := /bin/bash

install:
	@poetry install

clean:
	@rm -r ./dist

test:
	@poetry run pytest

build:
	@poetry build
