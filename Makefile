run:
	pipenv run ./dicompyler_app.py

init:
	pipenv install --dev --skip-lock

build:
	rm -rf dist && pipenv run pyinstaller app.onefile.spec

clean:
	rm -rf build dist

.PHONY: build clean init
