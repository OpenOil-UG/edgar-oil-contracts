#encoding: utf-8
import codecs

countryfile = '/tmp/countries.txt'
inputfile = '/tmp/oilgas.csv'
countries = ["Afghanistan","Albania","Algeria","Angola","Antigua And Barbuda","Argentina","Armenia","Austria","Azerbaijan","Bahamas","Bahrain","Bangladesh","Barbados","Belarus","Belize","Benin","Bhutan","Bolivia","Bosnia And Herzegovina","Botswana","Brazil","Brunei Darussalam","Bulgaria","Burkina Faso","Burundi","Cambodia","Cameroon","Canada","Cape Verde","Central African Republic","Chad","Chile","China","Christmas Island","Colombia","Comoros","Congo","Congo, The Democratic Republic Of The","Costa Rica","CÔte D'ivoire","Croatia","Cuba","Cyprus","Czech Republic","Denmark","Djibouti","Dominica","Dominican Republic","Ecuador","Egypt","El Salvador","Equatorial Guinea","Eritrea","Estonia","Ethiopia","Falkland Islands (malvinas)","Faroe Islands","Fiji","Finland","France","French Guiana","French Polynesia","Gabon","Gambia","Georgia","Germany","Ghana","Gibraltar","Greece","Greenland","Guatemala","Guinea","Guinea-bissau","Guyana","Haiti","Honduras","Hong Kong","Hungary","Iceland","India","Indonesia","Iran","Iraq","Ireland","Israel","Italy","Jamaica","Japan","Jordan","Kazakhstan","Kenya","Korea, Democratic People's Republic Of","Korea, Republic Of","Kuwait","Kyrgyzstan","Lao People's Democratic Republic","Latvia","Lebanon","Lesotho","Liberia","Libyan Arab Jamahiriya","Lithuania","Madagascar","Malawi","Malaysia","Maldives","Mali","Malta","Mauritania","Mauritius","Mexico","Moldova","Mongolia","Montenegro","Morocco","Mozambique","Myanmar","Namibia","Nepal","Netherlands","Nicaragua","Niger","Nigeria","Norway","Oman","Pakistan","Panama","Papua New Guinea","Paraguay","Peru","Philippines","Poland","Portugal","Qatar","Romania","Russian Federation","Rwanda","Sao Tome And Principe","Saudi Arabia","Senegal","Seychelles","Sierra Leone","Singapore","Slovakia","Slovenia","Somalia","South Africa","Soviet Union","Spain","Sri Lanka","Sudan","Suriname","Swaziland","Sweden","Syrian Arab Republic","Taiwan","Tajikistan","Tanzania, United Republic Of","Thailand","Timor-leste","Togo","Tonga","Trinidad And Tobago","Tunisia","Turkey","Turkmenistan","Uganda","Ukraine","United Arab Emirates","United Kingdom","United States","Uruguay","Uzbekistan","Venezuela","Viet Nam","Western Sahara","Yemen","Zambia","Zimbabwe"];
outputfile = '/tmp/oilgas_with_countries.csv'


if __name__ == '__main__':
    for line in codecs.open(inputfile, 'r', 'utf-8'):
        found = ''
        lowered = line.lower()
        for country in countries:
            country = country.decode('utf-8')
            if country.lower() in lowered:
                found = country
                break
        one, two = lowered.strip().split(',', 1)
        print('%s,"%s",%s' % (one,two, found))
    

