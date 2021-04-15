run:
	venv/Scripts/python app/run.py

load_fixture:
	@venv/Scripts/python app/load_fixture.py

test:
	@venv/Scripts/python -m pytest tests/test.py -vv -s --durations=5