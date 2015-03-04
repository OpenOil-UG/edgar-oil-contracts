# SEC EDGAR Oil Contracts Finder

This project aims to find full oil contract bodies among the filings submitted by
oil companies to the American stock regulator.

We've used a variety of approaches:

* Download and store SEC filings in the appropriate SIC classes using a Hadoop
  cluster. The resulting corpus is a JSON stream with an entry for each
  document filed since 1995.
* Score the documents using a second Hadoop cluster by counting terms that
  indicate an oil contract. The score is considered both normalized over
  the number of total words in the filed document, and as an absolute
  number (we actually want to bias for long texts).

We've also used a set of confirmed postive and negative matches to
generate a set of "watershed" terms which occur only in the contract
documents and not in any others. This was used to generate a search list
automatically, for a second phase of ranking.

# Setup

```
git clone https://github.com/danohuiginn/edgar-oil-contracts.git
cd edgar-oil-contracts
mkvirtualenv openoil
pip install -r requirements.txt
python setup.py develop
```

# Overview of usage

Most processes can be run through the makefile.

You will probably want to change some of the variables at the top of the Makefile, for instance to set appropriate paths for your system.

The current setup assumes there is a directory /data, which is writeable by the user running the makefile




# The pipeline

## List companies by SIC

First, get a list of all companies with the SICs (industry classifications) you are interested.
Put the SICs into **sics.txt**, one per line

```
make sic_companies
```

This writes data/companies_by_sic.txt a tab-separated file. Most important are the first 2 columns, giving us the CIK (company identifier), and the current name of the company:

```
1194506	ACREX VENTURES LTD	  	1000
```

# Download indices of all filings

The SEC provides quarterly index files, listing all files according to the company responsible for them. We want to download these

```
make index_files
```

This will download the company indices (as zip files) into ./company_listings, and also upload them to S3

Each line in an index looks like:

```
1001385|NORTHWEST PIPE CO|10-Q|2010-11-15|edgar/data/1001385/0001193125-10-260940.txt
```

Now we use [filter_filings.py](filter_filings.py) to select just the lines from companies we are interested in. These get written into the **company_listings_filtered** directory, and also uploaded to S3

```
make filter_filings
```

# Download the filings themselves

This is the time-consuming bit:

```
make dl_filings
```


# Finding contracts

To find contracts among edgar filings, we:

1) manually collect some example contracts, as well as some example non-contract filings
2) generate a list of phrases which appear more frequently among contracts than non-contracts
3) count how many times each of these phrases appear in our downloaded edgar filings. Generate a one-line json document for each matching document, showing the matching terms in context
4) convert that json file into csv
5) (manually) upload that csv file to google docs for review


# Generating the watershed list

put positive and negative examples in training/data/positive and training/data/negative

```
make build_watershed_list
```



# Working with google sheets

We use google docs for output and review of contents.

You will need a google account with access to the spreadsheets we are using

Edit dissect/sheets.py to use your google login details (GUSER, GPS). To avoid accidentally committing sensitive information to github, you may want to put them in another file and import

To refer to the sheets, you need to look at the ID in the url. e.g. if the URL is
https://docs.google.com/spreadsheets/d/1TOZfW0RI8K178v5mm_6vZBvILiGfIW5hLSDO5vCDQRM/

the ID is 1TOZfW0RI8K178v5mm_6vZBvILiGfIW5hLSDO5vCDQRM

These IDS are in a dict in `dissect/sheets.py:SHEETS`


## Finding company names

We collect company names from EITI reporting at 
https://docs.google.com/spreadsheets/d/1TOZfW0RI8K178v5mm_6vZBvILiGfIW5hLSDO5vCDQRM

Company names go in column A.

Run `make namesearch`. This will generate a regex from each sheet in column B. If you want to override any of these, you can put a replacement regex in column C, which will overrule anything in column B. To not search a company name, put in an impossible regex (e.g. .^). You may want this if the company name is also a common word, to avoid false positives.




Contact:

* @Open_Oil, @pudo
