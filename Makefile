.PHONY: all install lint run index \
		search search_dataset_code \
		search_dataset_docs answer \
		answer_dataset_code answer_dataset_docs \
		evaluate_code evaluate_docs debug clean

DATA_DIR := data
DATASET_DIR := $(DATA_DIR)/datasets
OUTPUT_DIR := $(DATA_DIR)/output

ANSWERED_DIR := $(DATASET_DIR)/AnsweredQuestions
UNANSWERED_DIR := $(DATASET_DIR)/UnansweredQuestions

SEARCH_RESULTS_DIR := $(OUTPUT_DIR)/search_results/UnansweredQuestions
ANSWERS_RESULTS_DIR := $(OUTPUT_DIR)/search_results_and_answer/UnansweredQuestions

CODE_DATASET := dataset_code_public.json
DOCS_DATASET := dataset_docs_public.json

DATASET_CODE_PATH := $(UNANSWERED_DIR)/$(CODE_DATASET)
DATASET_DOCS_PATH := $(UNANSWERED_DIR)/$(DOCS_DATASET)

EVAL_CODE_PATH := $(ANSWERED_DIR)/$(CODE_DATASET)
EVAL_DOCS_PATH := $(ANSWERED_DIR)/$(DOCS_DATASET)

SEARCH_CODE_RESULTS := $(SEARCH_RESULTS_DIR)/$(CODE_DATASET)
SEARCH_DOCS_RESULTS := $(SEARCH_RESULTS_DIR)/$(DOCS_DATASET)

K := 10

all: install lint run 

install:
	uv sync

run: index search_dataset_code search_dataset_docs evaluate_code evaluate_docs

index:
	python3 -m src index --max_chunk_size 2000

search:
	python3 -m src search "What is the AI?" --k $(K)

search_dataset_code:
	python3 -m src search_dataset \
		--dataset_path $(DATASET_CODE_PATH) \
		--k $(K) \
		--save_directory $(SEARCH_RESULTS_DIR)

search_dataset_docs:
	python3 -m src search_dataset \
		--dataset_path $(DATASET_DOCS_PATH) \
		--k $(K) \
		--save_directory $(SEARCH_RESULTS_DIR)

answer:
	python3 -m src answer "What is the AI?" --k $(K)

answer_dataset_code:
	python3 -m src answer_dataset \
		--student_search_results_path $(SEARCH_CODE_RESULTS) \
		--save_directory $(ANSWERS_RESULTS_DIR)

answer_dataset_docs:
	python3 -m src answer_dataset \
		--student_search_results_path $(SEARCH_DOCS_RESULTS) \
		--save_directory $(ANSWERS_RESULTS_DIR)

evaluate_code:
	python3 -m src evaluate \
		--student_search_results_path $(SEARCH_CODE_RESULTS) \
		--dataset_path $(EVAL_CODE_PATH)

evaluate_docs:
	python3 -m src evaluate \
		--student_search_results_path $(SEARCH_DOCS_RESULTS) \
		--dataset_path $(EVAL_DOCS_PATH)

moulinette_docs_eval:
	./moulinette evaluate_student_search_results \
	$(SEARCH_DOCS_RESULTS) \
	$(EVAL_DOCS_PATH) \
	--k $(K)

lint:
	flake8 src
	mypy src --warn-return-any --warn-unused-ignores \
		--ignore-missing-imports --disallow-untyped-defs \
		--check-untyped-defs

debug:
	python3 -m pdb -m src index --max_chunk_size 2000

clean:
		rm -rf build
		rm -rf dist
		rm -rf __pycache__
		rm -rf .mypy_cache

