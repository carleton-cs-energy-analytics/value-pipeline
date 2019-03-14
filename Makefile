.PHONY: run email

run:
	python3 importers/siemens_importer.py

email: run
	TO_EMAIL="git@alextdavis.me" python3 email_alerts.py
