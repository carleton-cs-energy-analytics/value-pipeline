.PHONY: run email all

run:
	python3 importers/siemens_importer.py

email: run
	python3 email_alerts.py

all:
	python3 importers/siemens_importer.py all
