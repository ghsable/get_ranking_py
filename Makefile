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

# request: make init
lint:
	poetry run pyright $(SRC_FILE)
