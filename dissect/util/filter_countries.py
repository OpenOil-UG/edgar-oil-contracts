#encoding: utf-8

'''
Identify countries mentioned within a csv file

Input: csv with
 [ignored col], text

Output: csv with
 [ignored col], text, extracted country name, extracted search term
'''

import codecs
import csv
import pycountry
import sys

#inputfile = '/tmp/oilgasheadlines.csv'
#outfile = '/tmp/oilgasheadlines_countries.csv'
countries = ["Afghanistan","Albania","Algeria","Angola","Antigua And Barbuda","Argentina","Armenia","Austria","Azerbaijan","Bahamas","Bahrain","Bangladesh","Barbados","Belarus","Belize","Benin","Bhutan","Bolivia","Bosnia And Herzegovina","Botswana","Brazil","Brunei Darussalam","Bulgaria","Burkina Faso","Burundi","Cambodia","Cameroon","Canada","Cape Verde","Central African Republic","Chad","Chile","China","Christmas Island","Colombia","Comoros","Congo","Congo, The Democratic Republic Of The","Costa Rica","CÔte D'ivoire","Croatia","Cuba","Cyprus","Czech Republic","Denmark","Djibouti","Dominica","Dominican Republic","Ecuador","Egypt","El Salvador","Equatorial Guinea","Eritrea","Estonia","Ethiopia","Falkland Islands (malvinas)","Faroe Islands","Fiji","Finland","France","French Guiana","French Polynesia","Gabon","Gambia","Georgia","Germany","Ghana","Gibraltar","Greece","Greenland","Guatemala","Guinea","Guinea-bissau","Guyana","Haiti","Honduras","Hong Kong","Hungary","Iceland","India","Indonesia","Iran","Iraq","Ireland","Israel","Italy","Jamaica","Japan","Jordan","Kazakhstan","Kenya","Korea, Democratic People's Republic Of","Korea, Republic Of","Kuwait","Kyrgyzstan","Lao People's Democratic Republic","Latvia","Lebanon","Lesotho","Liberia","Libyan Arab Jamahiriya","Lithuania","Madagascar","Malawi","Malaysia","Maldives","Mali","Malta","Mauritania","Mauritius","Mexico","Moldova","Mongolia","Montenegro","Morocco","Mozambique","Myanmar","Namibia","Nepal","Netherlands","Nicaragua","Nigeria","Niger","Norway","Oman","Pakistan","Panama","Papua New Guinea","Paraguay","Peru","Philippines","Poland","Portugal","Qatar","Romania","Russian Federation","Rwanda","Sao Tome And Principe","Saudi Arabia","Senegal","Seychelles","Sierra Leone","Singapore","Slovakia","Slovenia","Somalia","South Africa","Soviet Union","Spain","Sri Lanka","Sudan","Suriname","Swaziland","Sweden","Syrian Arab Republic","Taiwan","Tajikistan","Tanzania, United Republic Of","Thailand","Timor-leste","Togo","Tonga","Trinidad And Tobago","Tunisia","Turkey","Turkmenistan","Uganda","Ukraine","United Arab Emirates","United Kingdom","United States","Uruguay","Uzbekistan","Venezuela","Viet Nam","Western Sahara","Yemen","Zambia","Zimbabwe"]


outputfile = '/tmp/oilgas_with_countries.csv'

def get_search_terms():
    '''
    Return a dictionary of lists
     country-name, search terms
    

      Country names of the world
      Subdivisions of US and Canada    
    '''
    terms = {}
    for country in pycountry.countries:
        searchterms = [country.name]
        if ',' in country.name:
            # for 'korea, north' search 'north korea'
            searchterms.append(' '.join(reversed(country.name.split(', '))))
        if country.alpha2 in ('US', 'CA'):
            searchterms += [x.name for x in pycountry.subdivisions.get(country_code = country.alpha2)]
        searchterms = [x.lower() for x in searchterms]
        terms[country.name] = searchterms

    # and some manual tweaks
    terms['Niger'] = ['niger ']
    terms['United Kingdom'].append(' uk ')
    terms['United States']+= [' usa', ' us ']
    terms['Trinidad and Tobago'].append('trinidad')
    return terms

def search_basic():
    '''
    This is the old version, that just searches by country name
    '''
    outf = csv.writer(sys.stdout)
    #outf = csv.writer(codecs.open(outfile, 'w', 'utf-8'))
    #csv.reader(codecs.open(inputfile, 'r', 'utf-8')):
    inf = csv.reader(sys.stdin)
    for line in inf:
        found = ''
        if len(line) < 2:
            continue
        lowered = line[1].lower()
        for country in countries:
            #country = country.decode('utf-8')
            if country.lower() in lowered:
                found = country
                break
        line.append(found)
        outf.writerow(line)
        #one, two = lowered.strip().split(',', 1)
        #print('%s,"%s",%s' % (one,two, found))
    
def search_with_subdivisions():
    outf = csv.writer(sys.stdout)
    inf = csv.reader(sys.stdin)
    searchterms = get_search_terms()
    for line in inf:
        countryname, searchterm = '',''
        if len(line) < 2:
            continue
        lowered = line[1].lower()
        for country, terms in searchterms.items():
            #country = country.decode('utf-8')
            for term in terms:
                if term in lowered:
                    countryname, searchterm = country, term
                    break
        line.append(countryname)
        line.append(searchterm)
        outf.writerow(line)
        #one, two = lowered.strip().split(',', 1)
        #print('%s,"%s",%s' % (one,two, found))

if __name__ == '__main__':
    search_with_subdivisions()

