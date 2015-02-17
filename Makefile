
BUCKET=s3://sec-mining.openoil.net
CONF_FILE=mrjob.conf

FILING_DOWNLOAD_DIR=/data/edgar_filings
EXTRACTED_TEXT_DIR=/data/edgar_filings_text
WATERSHED_FILE=watershed_list.txt
WATERSHED_FILE_LICENSES=watershed_list_licenses.txt
SCORE_FILE=computed_scores.txt
SCORE_FILE_LICENSES=computed_scores_licenses.txt
RESULT_CSV_FILE=data/license_matches.txt
COMPANY_LIST=data/companies_by_sic.txt
SIC_LIST=data/sics.txt

SEDAR_SCORE_FILE=/tmp/scored_sedar.json
SEDAR_RESULT_FILE=/tmp/sedar_results.csv
SEDAR_DL_DIR=/data/sedar/mining_material_documents_2014


#####
#
#  LEGACY CODE SECTION
#
#   the following operations were used for the oil scraping in Oct 2014
#   they may or may not still work
#
#####


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

dl_filings_test:
	head -20 filings_by_company.txt | python dl_filings.py --outdir $(FILING_DOWNLOAD_DIR)

text_extract:
	python util/edgar_text_extract.py --filingdir $(FILING_DOWNLOAD_DIR) --outdir $(EXTRACTED_TEXT_DIR)

#####
#
# Active commands as of Feb 2015
#
#   These commands were working (albeit temperamentally) in Feb 2015
#   See README.txt for details, or ask Dan
#
#####


# Generate a list of all companies which belong to some SICs
#  i.e. all companies in certain industries
# This version will work without access to hadoop or Amazon EMR...
sic_companies:
	cat $(SIC_LIST) | python companies_by_sic.py > $(COMPANY_LIST)

index_files:
	python edgar_indices.py
	aws s3 sync ./company_listings $(BUCKET)/company_listings

filter_filings:
	python filter_filings.py
	aws s3 sync ./company_listings_filtered $(BUCKET)/company_listings_filtered


# ...and this version (should) work remotely, but is buggy
#sic_companies_remote:
#	python companies_by_sic.py \
#		--conf-path $(CONF_FILE) \
#		--no-output \
#		--runner local \
#		--cleanup NONE \
#		-v \
#		--emr-job-flow-id j-HRW9YVFAQ91Y\
#		--output-dir=$(BUCKET)/moresics4 < sics.txt

minerals_reports:
	# zless company_listings/master_2014_* | grep "|SD|" > sd_filings.txt
	aws s3 sync ./sdfilings $(BUCKET)/minerals_reports

dl_filings:
	cat filings_by_company.txt | python dl_filings.py --outdir $(FILING_DOWNLOAD_DIR)

watershed_list_mining_basic:
	python training/watershed.py --pos_dir training/data_mining/positive --neg_dir training/data/negative> $(WATERSHED_FILE)

watershed_list_mining_licenses:
	python training/watershed.py --threshold 3 --pos_dir training/licenses/positive --neg_dir training/data/negative > $(WATERSHED_FILE_LICENSES)

score_by_filename:
	ls -1d $(EXTRACTED_TEXT_DIR)/*txt | python score_filings.py | tee $(SCORE_FILE)

score_licenses:
	ls -1d $(EXTRACTED_TEXT_DIR)/*txt | python score_filings.py | tee $(SCORE_FILE_LICENSES)

score_pdfs:
	find $(SEDAR_DL_DIR) -type f | python score_filings.py | tee $(SEDAR_SCORE_FILE)

reduce_sedar:
	less $(SEDAR_SCORE_FILE) | jq --raw-output '"\(.score),\(.filepath),\(.positives),{\(.country_names)}"' | sort -rn | sed -e 's/\/data\/sedar/https:\/\/sedar.openoil.net.s3.amazonaws.com/' -e "s/{/\'{/g" -e "s/}/}\'/g" > $(SEDAR_RESULT_FILE)


reduce_results:
	less $(SCORE_FILE) | jq --raw-output '"\(.score),\(.filepath)"' | sort -rn | head -n 1000 |cut -d, -f 2 | python edgar_link.py > $(RESULT_CSV_FILE)
