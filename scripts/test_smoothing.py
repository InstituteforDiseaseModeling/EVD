from format_for_DTK import get_all_counts
import pandas as pd
import matplotlib.pyplot as plt
import datetime
import json

all_counts=get_all_counts()
print(all_counts.head())

def smooth():
    minor=['Dallas','New York','Glasgow','Madrid']
    plt.figure('smoothed')
    ax=all_counts[minor].plot(alpha=0.5,ax=plt.gca())
    converted = all_counts.asfreq('D', method='bfill')
    smoothed = pd.ewma(converted,span=21)
    smoothed[minor].plot(ax=ax)
    print(smoothed[-10:])
    return smoothed

def aggregate(smoothed):
    dfsum=smoothed.sum(axis=1)
    df=pd.DataFrame(dfsum,columns=['EbolaCases'])
    df['CumulativeEbolaCases']=dfsum.cumsum()
    print(df[-10:])
    plt.figure('aggregated')
    df['EbolaCases'].plot()
    return df

def write_inset_chart(channels):
    header={'DateTime':str(datetime.datetime.now()),
            'Timesteps':len(channels),
            'Channels':len(channels.keys())}
    data_channels={k:{'Units':'','Data':v.tolist()} for k,v in channels.iteritems()}
    with open('InsetChart.json','w') as ic:
        json.dump({'Header':header,'Channels':data_channels},ic,indent=2)

smoothed=smooth()
channels=aggregate(smoothed)
write_inset_chart(channels)
#plt.show()
