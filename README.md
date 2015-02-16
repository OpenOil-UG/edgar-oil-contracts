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

# Generating the watershed list

put positive and negative examples in training/data/positive and training/data/negative
python watershed.py


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





Contact:

* @Open_Oil, @pudo
