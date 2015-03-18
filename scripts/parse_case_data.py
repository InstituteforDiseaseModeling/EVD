import os
import json
import csv
from datetime import datetime

def week_of_date(date_input):
    date_object = datetime.strptime(date_input, '%m/%d/%Y')
    weekno =  date_object.isocalendar()[1]
    year = date_object.isocalendar()[0]
    if year == 2015:
        weekno = weekno + 52
    return weekno - 11 #shifting the ranges to Mar 2014 - Mar 2015

def read_case_counts(csv_file):
    case_counts={}
    with open(os.path.join('..','data',csv_file),'rb') as f:
        reader=csv.reader(f)
        header=reader.next()
        fields=[f.replace("'","") for f in header]
        print(fields[1:])
        for district in fields[1:]:
            case_counts[district]=[0 for w in range(52)] ##TODO: remove hard coded weeks here
        for row in reader:
            date=row[0]
            week=week_of_date(date)
            print(date,week)
            if week >0:
                for col in range(1,len(fields)):
                    cases=row[col]
                    #print(col,cases)
                    if cases:
                        #print(fields[col],week-1,int(float(cases)))
                        case_counts[fields[col]][week-1]+=int(float(cases))
                        #print(case_counts[fields[col]][week-1])

         # cumulative counts
        for dist,counts in case_counts.items():
            if 'Cumulative' not in case_counts:
                case_counts['Cumulative']={}
            if 'Recent' not in case_counts:
                case_counts['Recent']={}
            #print(dist,counts)
            case_counts['Cumulative'][dist]=sum(counts)
            case_counts['Recent'][dist]=sum(counts[-6:]) # last six weeks

    return case_counts

iso_by_country={'Guinee':'GIN',
                'Sierra_Leone':'SLE',
                'Liberia':'LBR'}

def get_ebola_counts_by_country(countries):
    cases={}
    for country in countries:
        iso=iso_by_country[country]
        cases[iso]=read_case_counts(country+'_EVD_2014.csv') # Situation Reports (public)
        #cases[iso]=read_case_counts('case_reports_%s.csv' % country) # WHO VSHOC line list (confidential)
    return cases

if __name__=='__main__':
    countries=['Guinee','Sierra_Leone','Liberia']
    cases = get_ebola_counts_by_country(countries)
    with open('tmp_weekly_cases.json','w') as f: json.dump(cases,f)
