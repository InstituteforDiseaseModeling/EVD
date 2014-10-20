import os
import json
import csv
from datetime import datetime
import matplotlib.pyplot as plt
import psycopg2
from plotting import adjust_spines

def week_of_date(date_input):
    date_object = datetime.strptime(date_input, '%m/%d/%Y')
    return date_object.isocalendar()[1]

def read_case_counts(csv_file):
    case_counts={}
    with open(os.path.join('..','data',csv_file),'rb') as f:
        reader=csv.reader(f)
        header=reader.next()
        fields=[f.replace("'","") for f in header]
        print(fields[1:])
        for district in fields[1:]:
            case_counts[district]=[0 for w in range(52)]
        for row in reader:
            date=row[0]
            week=week_of_date(date)
            print(date,week)
            for col in range(1,len(fields)):
                cases=row[col]
                #print(col,cases)
                if cases:
                    #print(fields[col],week-1,int(float(cases)))
                    case_counts[fields[col]][week-1]+=int(float(cases))
                    #print(case_counts[fields[col]][week-1])
    return case_counts

def get_ebola_counts_by_country(countries):
    cases={}
    for country in countries:
        cases[country]=read_case_counts(country+'_EVD_2014.csv')
    return cases

week_numbers = [0.5+w for w in range(52)]
first_day_of_months = [0,31,59,90,120,151,181,212,243,273]#,304,334]
week_number_of_first_of_month=[d/7.0 for d in first_day_of_months]
def plot_site(ax,country,district,color,labels=['left'], max_week_scale=50):
    plt.bar(week_numbers, cases[country][district], width=0.8, color=color, alpha=0.5)
    adjust_spines(ax,labels)
    plt.xlim([0.5,42.5]) # weeks into early October
    plt.ylim([0,max(max_week_scale,max(cases[country][district])+1)]) # closer to equal scaling
    #plt.yticks(range(0,350,50))
    plt.yticks([min(cases[country][district]), max(cases[country][district])])
    if 'bottom' in labels:
        plt.xticks(week_number_of_first_of_month)
        #print(week_number_of_first_of_month)
        ax.xaxis.set_ticklabels(['Jan','Feb','Mar','Apr','May','Jun','Jul','Aug','Sep','Oct'])#,'Nov','Dec'])
    plt.text(0.5,10,district,fontsize=10,color=color,va='bottom',ha='left')

cases = get_ebola_counts_by_country(['Guinee','Sierra_Leone','Liberia'])

sitesW=[
        ('Guinee','Conakry','#1111aa'),
        ('Sierra_Leone','Bombali','#114411'),
        ('Sierra_Leone','Port Loko','#226622'),
        ('Sierra_Leone','Western (urban)','#229922'),
        ('Sierra_Leone','Western (rural)','#229922'),
        ('Sierra_Leone','Bo','#88dd88'),
        ('Sierra_Leone','Kenema','#99bb99'),
        ('Sierra_Leone','Kailahun','#668866',['bottom','left'])
        ]

sitesE=[
        ('Guinee','Gueckedou','#8888ee'),  
        ('Guinee','Macenta','#7755cc'),
        ('Guinee','NZerekore','#8866aa'),
        ('Liberia','Lofa','#aa2266'),
        ('Liberia','Margibi','#aa2222'),
        ('Liberia','Montserrado','#882222'),
        ('Liberia','Bong','#884444'),
        ('Liberia','Nimba','#886666',['bottom','left'])
        ]

def plot_group_of_districts(group):
    for i,site in enumerate(group):
        ax=plt.subplot(len(group),1,i+1)
        plot_site(ax,*site, max_week_scale=80)
    plt.tight_layout()    

if __name__=='__main__':
    plt.figure('Ebola cases West', figsize=(5,9), facecolor='w')
    plot_group_of_districts(sitesW)

    plt.figure('Ebola cases East', figsize=(5,9), facecolor='w')
    plot_group_of_districts(sitesE)

    #with open('../model/disease/weekly_cases.json','w') as f: json.dump(cases,f)

    plt.show()
