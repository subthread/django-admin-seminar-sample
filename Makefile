SOURCE_DIR := src/
target ?= ${SOURCE_DIR}

poetry := poetry
#poetry := docker compose exec -T server poetry


.PHONY: reformat check black isort flake8 fix-file

reformat: black isort

check:
	@echo check black
	@${poetry} run black --check ${SOURCE_DIR} --quiet
	@echo check isort
	@${poetry} run isort --check ${SOURCE_DIR} --quiet
	@echo check flake8
	@${poetry} run pflake8       ${SOURCE_DIR}  # --quiet

black:
	${poetry} run black ${SOURCE_DIR}

isort:
	${poetry} run isort ${SOURCE_DIR}

flake8:
	${poetry} run pflake8 ${SOURCE_DIR}

fix-file:
	${poetry} run black   "${target}"
	${poetry} run isort   "${target}"
	${poetry} run pflake8 "${target}"
