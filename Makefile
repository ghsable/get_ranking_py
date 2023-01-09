$(eval SRC_DIR := ./get_ranking_py)
$(eval DOCS_DIR := ./docs)
$(eval SRC_FILE := ./get_ranking_py/main.py)
$(eval DATA_FILE := ./get_ranking_py/data/game_score_log.csv)

.SILENT:

init:
	poetry add pyright Sphinx

shell:
	poetry shell

run:
	python $(SRC_FILE) $(DATA_FILE)

run_p:
	poetry run $(SRC_FILE) $(DATA_FILE)

# <--- request: make init ---> #

lint:
	poetry run pyright $(SRC_FILE)

sphinx-init:
	poetry run sphinx-apidoc -F -H project -A Helve -V v1.0 -o $(DOCS_DIR) $(SRC_DIR)

sphinx-build:
	poetry run sphinx-build $(DOCS_DIR) $(DOCS_DIR)/_build

