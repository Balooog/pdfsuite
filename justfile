set shell := ["bash", "-uc"]

doctor:
	python scripts/doctor.py

run *args:
	pdfsuite {{args}}

smoke:
	bash scripts/smoke_test.sh
