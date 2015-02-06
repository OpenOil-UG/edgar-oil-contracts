
BUCKET=s3://sec-mining.openoil.net
CONF_FILE=mrjob.conf

_make_listing:
	python generate_input.py
	rm -rf tasks
	mkdir tasks
	split -l 10 listing.txt tasks/listing

test_import:
	python import_filings.py --cleanup=NONE --no-output <test_listing.txt

test_sic_filter:
	python sic_filter_filings.py --cleanup=NONE --no-output <filings.txt

test_score:
	python score_filings.py --cleanup=NONE --no-output <filings.txt

import:
	python import_filings.py -r emr \
		--conf-path $(CONF_FILE) \
		--output-dir=$(BUCKET)/filings-13xx/ \
		--no-output \
		$(BUCKET)/tasks/

sic_filter:
	python sic_filter_filings.py -r emr \
		--conf-path $(CONF_FILE) \
		--output-dir=$(BUCKET)/filings-13xx/ \
		--no-output \
		$(BUCKET)/filings-all/

score:
	python score_filings.py -r emr \
		--conf-path $(CONF_FILE) \
		--output-dir=$(BUCKET)/scores/ \
		--no-output \
		--file searches.txt --file stopwords.txt \
		$(BUCKET)/filings-sample/


make_listing:
	rm -rf tasks
	mkdir tasks
	python generate_input.py | split -l 10 - tasks/listing
	aws s3 sync ./tasks/ $(BUCKET)/tasks/
