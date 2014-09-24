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
    with open(csv_file,'rb') as f:
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
first_day_of_months = [0,31,59,90,120,151,181,212,243]#,273,304,334]
week_number_of_first_of_month=[d/7.0 for d in first_day_of_months]
def plot_site(ax,country,district,color,labels=['left']):
    plt.bar(week_numbers, cases[country][district], width=0.8, color=color, alpha=0.5)
    adjust_spines(ax,labels)
    plt.xlim([0.5,38.5]) # weeks to mid-September
    #plt.ylim([0,max(50,max(cases[country][district])+1)])
    #plt.yticks(range(0,150,50))
    plt.yticks([min(cases[country][district]), max(cases[country][district])])
    if 'bottom' in labels:
        plt.xticks(week_number_of_first_of_month)        
        #print(week_number_of_first_of_month)
        ax.xaxis.set_ticklabels(['Jan','Feb','Mar','Apr','May','Jun','Jul','Aug','Sep'])#,'Oct','Nov','Dec'])
    plt.text(0.5,10,district,fontsize=10,color=color,va='bottom',ha='left')

cases = get_ebola_counts_by_country(['Guinee','Sierra_Leone','Liberia'])

sites=[ #('Liberia','Lofa','salmon'),
        #('Liberia','Montserrado','darkred'),
        #('Liberia','Margibi','r'),
        #('Liberia','Nimba','r'),
        #('Liberia','Bong','r'),        
        ('Sierra_Leone','Kailahun','darkseagreen'),
        ('Sierra_Leone','Kenema','g'),
        ('Sierra_Leone','Kono','lightgreen'),
        ('Sierra_Leone','Bo','forestgreen'),
        ('Sierra_Leone','Bombali','g'),                
        ('Sierra_Leone','Western (urban)','olive'),
        ('Sierra_Leone','Western (rural)','olivedrab'),        
        ('Sierra_Leone','Port Loko','darkolivegreen',['bottom','left'])
        #('Guinee','Conakry','darkblue'),
        #('Guinee','Macenta','b'),
        #('Guinee','Gueckedou','dodgerblue',['bottom','left'])
        ]

plt.figure('Ebola cases', figsize=(8,8), facecolor='w')
for i,site in enumerate(sites):
    ax=plt.subplot(len(sites),1,i+1)
    plot_site(ax,*site)

#plt.xlabel('Week of 2014')
plt.tight_layout()
plt.show()
