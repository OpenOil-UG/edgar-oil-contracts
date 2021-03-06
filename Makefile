
## Flags
# do we upload everything to S3
S3SYNC=false
#INDUSTRY=oil

ROOTDIR=/data
BASEDIR=$(ROOTDIR)/$(INDUSTRY)

#SHELL=/bin/bash
BUCKET=s3://sec-mining.openoil.net
CONF_FILE=mrjob.conf


COMPANY_LIST=$(BASEDIR)/companies_by_sic_$(INDUSTRY).txt

SIC_LIST=sics_$(INDUSTRY).txt


# where to put the edgar indices. This crosses both oil and mining
COMPANY_LISTINGS_DIR=$(ROOTDIR)/company_listings

# listings of every filing from a company we are interested in
COMPANY_LISTINGS_FILTERED_DIR=$(BASEDIR)/company_listings_filtered



FILING_DOWNLOAD_DIR=$(BASEDIR)/edgar_filings
EXTRACTED_TEXT_DIR=$(BASEDIR)/edgar_filings_text

# where to put known contracts in pdf, html, etc formats
# nb dir managed using barn (https://github.com/pudo/barn)
TRAINING_POSITIVE_RAW_DIR=/tmp/contracts_raw 

# where to put extracted text of known contracts
TRAINING_POSITIVE_DIR=/tmp/contracts_positive

WATERSHED_FILE=watershed_list.txt
WATERSHED_FILE_LICENSES=watershed_list_licenses.txt
SCORE_FILE=/tmp/computed_scores_$(INDUSTRY).txt
SCORE_FILE_LICENSES=/tmp/computed_scores_licenses_$(INDUSTRY).txt
RESULT_CSV_FILE=data/license_matches.txt


SEDAR_SCORE_FILE=/tmp/scored_sedar.json
SEDAR_RESULT_FILE=/tmp/sedar_results.csv
#SEDAR_DL_DIR=/data/sedar/mining_material_documents_2005
SEDAR_DL_DIR=/data/sedar/mining_material*




WORDSEARCH_REGEXFILE=/tmp/company_name_regexes.txt
WORDSEARCH_RESULTFILE=/tmp/company_name_results.json



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

sic_companies:
	cat $(SIC_LIST) | python dissect/companies_by_sic.py > $(COMPANY_LIST)


# this works for all cases
index_files:
	python dissect/edgar_indices.py --output-dir $(COMPANY_LISTINGS_DIR)
	if [ $(S3SYNC) = "true" ]; then \
		aws s3 sync $(COMPANY_LISTINGS_DIR) $(BUCKET)/company_listings ; \
	fi


filter_filings:
	python dissect/filter_filings.py --input_dir $(COMPANY_LISTINGS_DIR) --output_dir $(COMPANY_LISTINGS_FILTERED_DIR) --company_list $(COMPANY_LIST)
	if [ $(S3SYNC) = "true" ]; then \
	  aws s3 sync $(COMPANY_LISTINGS_FILTERED_DIR) $(BUCKET)/company_listings_filtered; \
	fi

dl_filings:
	find $(COMPANY_LISTINGS_FILTERED_DIR) | xargs cat | python dissect/dl_filings.py --outdir $(FILING_DOWNLOAD_DIR)


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


build_training_data:
	python dissect/diss.py build_training_data --barndir $(TRAINING_POSITIVE_RAW_DIR) --pos_dir $(TRAINING_POSITIVE_DIR) --include_text_directory /data/drivelicenses

build_watershed_list:
	python dissect/diss.py build_watershed --threshold 3 --pos_dir $(TRAINING_POSITIVE_DIR) --neg_dir training/data/negative --outfile $(WATERSHED_FILE)

score_by_filename:
	find $(EXTRACTED_TEXT_DIR) -type f | python dissect/score_filings.py -r local --jobconf mapred.map.tasks=10  | tee $(SCORE_FILE)

score_licenses:
	ls -1d $(EXTRACTED_TEXT_DIR)/*txt | python dissect/score_filings.py | tee $(SCORE_FILE_LICENSES)

score_pdfs:
	#find $(SEDAR_DL_DIR) -type f | python score_filings.py -r local --jobconf mapred.job.maps=10 | tee $(SEDAR_SCORE_FILE)
	find $(SEDAR_DL_DIR) -type f | python score_filings.py -r local --jobconf mapred.map.tasks=10 | tee $(SEDAR_SCORE_FILE)


wordmatch:
	find $(SEDAR_DL_DIR) -type f | python wordsearcher.py -r local --jobconf mapred.map.tasks=10 | tee /tmp/wordmatches.txt

reduce_sedar_old:
	less $(SEDAR_SCORE_FILE) | jq --raw-output '"\(.score),\(.filepath),¬\(.positives)¬,¬\(.country_names)¬,¬\(.extract)¬"' | sort -rn | sed -e 's/\/data\/sedar/https:\/\/sedar.openoil.net.s3.amazonaws.com/' -e "s/¬/\'/g" > $(SEDAR_RESULT_FILE)

reduce_sedar:
	less $(SEDAR_SCORE_FILE) | python dissect/postprocess_json.py --include_old_reviews > $(SEDAR_RESULT_FILE)

reduce_to_csv_oil:
	cat /tmp/computed_scores_oil.txt | python dissect/postprocess_json.py | sort -rn > /tmp/assignments_oil.csv

reduce_to_csv_mining:
	cat /tmp/computed_scores_mining.txt | python dissect/postprocess_json.py | sort -rn > /tmp/assignments_mining.csv

reduce_results:
	less $(SCORE_FILE) | jq --raw-output '"\(.score),\(.filepath)"' | sort -rn | head -n 5000 |cut -d, -f 2 | python dissect/edgar_link.py > $(RESULT_CSV_FILE)

namesearch:
	#python dissect/sheetnamesearch.py --filename $(WORDSEARCH_REGEXFILE) generate_searchterms
	find /data/oil/edgar_filings_text -type f | head -n 300 | python dissect/wordsearcher.py --searchterm-file=$(WORDSEARCH_REGEXFILE) --regex -r local --jobconf mapred.map.tasks=10 | tee $(WORDSEARCH_RESULTFILE)
	#python dissect/sheetnamesearch.py --filename $(WORDSEARCH_RESULTFILE) reconcile_results


text_extract:
	python dissect/util/edgar_text_extract.py --filingdir $(FILING_DOWNLOAD_DIR) --outdir $(EXTRACTED_TEXT_DIR)


grep_for_projects:
	# Build a list of every edgar filing that contains the word 'project' (capitalized)
	LC_ALL=C fgrep -rl "Project" /data/mining/edgar_filings_text/ /data/oil/edgar_filings_text | tee /tmp/edgar_filings_containing_project.txt

grep_for_projects_oil:
	# Build a list of every edgar filing that contains the word 'project' (capitalized)
	LC_ALL=C fgrep -rl "Project" /data/oil/edgar_filings_text | tee /tmp/edgar_filings_containing_project_oil.txt

grep_eiti_projects:
	LC_ALL=C fgrep -r -o --file eiti_projects_deduped.txt /data/oil/edgar_filings_text | tee /tmp/eiti_project_matches.txt

project_details_oil:
	cat /tmp/edgar_filings_containing_project_oil.txt | python dissect/projectsearch.py -r local --jobconf mapred.map.tasks=10 | tee /tmp/project_oil_details.csv


grep_assignment_preliminary:
	LC_ALL=C grep -E -i -r -o --file assignment_search_terms.txt /data/oil/edgar_filings_text /data/mining/edgar_filings_text /data/_pdftext_cache | tee /tmp/eiti_project_matches.txt


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

tardumps:
	rm /tmp/dissect_nested.tgz /tmp/dissect.tgz
	tar -czvf /tmp/dissect_nested.tgz --exclude dissect/training dissect
	tar -czvf /tmp/dissect.tgz --exclude=dissect/training dissect/*

proximity:
	python dissect/proximity.py --emr-job-flow-id=j-23Q7FYWE9VDOP -r emr -c /home/src/emrtest/mrjob.conf --python-archive /tmp/dissect.tgz --python-archive /tmp/dissect_nested.tgz --output-dir=s3://logs.openoil.net/emr_proximity_full /tmp/oilfilings.txt | tee /tmp/emrout_full

proximity_local:
	python dissect/proximity.py --emr-job-flow-id=j-23Q7FYWE9VDOP -r local -c /home/src/emrtest/mrjob.conf --python-archive /tmp/dissect.tgz --python-archive /tmp/dissect_nested.tgz /tmp/fewoilfilings.txt | tee /tmp/emrout

