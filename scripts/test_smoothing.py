from format_for_DTK import get_all_counts
import pandas as pd
import matplotlib.pyplot as plt

all_counts=get_all_counts()
print(all_counts.head())


ax=all_counts[['Montserrado','Conakry','Kailahun']].plot(alpha=0.5)
converted = all_counts.asfreq('D', method='bfill')
pd.ewma(converted[['Montserrado','Conakry','Kailahun']],span=21).plot(ax=ax)

print(converted.head())

plt.show()
