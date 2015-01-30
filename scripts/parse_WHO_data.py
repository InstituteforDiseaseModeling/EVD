import os
import json
import pandas as pd
from datetime import datetime

def format_time_span(epi_week):
    return datetime.strptime(' '.join(epi_week.split()[-3:]),'%d %B %Y')

def read_case_counts(csv_file,sources=[]):
    with open(os.path.join('..','data',csv_file),'rb') as f:
        cases=pd.read_csv(f)

    cases=cases.dropna(subset=['Location'])
    
    cases['Epi week']=cases['Epi week'].map(format_time_span)

    # Select sources to compare
    if sources:
        cases=cases[cases['Ebola data source'].isin(sources)]

    ## Group including Case definition split
    #cases.set_index(['Epi week','Location','Ebola data source','Case definition'],inplace=True)
    #cases_by_district=cases['Numeric'].unstack(['Location','Ebola data source','Case definition'])

    # Sum probable and confirmed
    cases=cases.groupby(['Epi week','Location','Ebola data source'])['Numeric'].sum()
    cases_by_district=cases.unstack(['Location','Ebola data source'])

    return cases_by_district

def get_ebola_counts_by_country(countries,sources=['Situation report','Patient database']):
    cases={}
    for iso in countries:
        cases[iso]=read_case_counts('data-text-'+iso+'.csv', 
                                    sources=sources)
    return cases

if __name__=='__main__':
    countries=['GIN','LBR']#'SLE'
    cases = get_ebola_counts_by_country(countries,sources=['Situation report'])

    GIN_ebola_districts=['CONAKRY','GUECKEDOU','MACENTA','DABOLA','KISSIDOUGO','DINGUIRAYE','TELIMELE','BOFFA',
            'KOUROUSSA','SIGUIRI','PITA',"N'ZEREKORE",'YOMOU','DUBREKA','FORECARIAH','KEROUANE','COYAH',
            'DALABA','BEYLA','KINDIA','LOLA','BOKE','FARANAH','KANKAN']

    LBR_ebola_districts=['BOMI','BONG','GBARPOLU','GRAND BASSA','GRAND CAPE MOUNT','GRAND GEDEH','GRAND KRU','LOFA','MARGIBI','MARYLAND','MONTSERRADO','NIMBA','RIVER GEE','RIVERCESS','SINOE']

    date_after=datetime(2014,12,1)

    GIN_sitrep_cases=cases['GIN'].ix[date_after:].swaplevel(0,1,axis=1)['Situation report'][GIN_ebola_districts]

    print(GIN_sitrep_cases)

    GIN_sitrep_cases.to_csv('tmp_GIN_cases.csv')

    LBR_sitrep_cases=cases['LBR'].ix[date_after:].swaplevel(0,1,axis=1)['Situation report'][LBR_ebola_districts]

    print(LBR_sitrep_cases)

    LBR_sitrep_cases.to_csv('tmp_LBR_cases.csv')
