from plot_ebola_cases import *
import matplotlib.pyplot as plt

sitesSierraLeone=[
        ('Sierra_Leone','Bombali','#114411'),
        ('Sierra_Leone','Port Loko','#226622'),
        ('Sierra_Leone','Western (urban)','#229922'),
        ('Sierra_Leone','Western (rural)','#229922'),
        ('Sierra_Leone','Kenema','#99bb99'),
        ('Sierra_Leone','Kailahun','#668866',['bottom','left'])
        ]

sitesMoreSierraLeone=[
        ('Sierra_Leone','Kambia','#8888ee'),  
        ('Sierra_Leone','Pujehun','#7755cc'),
        ('Sierra_Leone','Moyamba','#8866aa'),
        ('Sierra_Leone','Bo','#88dd88'),
        ('Sierra_Leone','Bonthe','#aa2266',['bottom','left'])
        ]

plt.figure('Ebola cases Sierra Leone', figsize=(5,9), facecolor='w')
plot_group_of_districts(sitesSierraLeone)

plt.figure('More Ebola cases Sierra Leone', figsize=(5,5), facecolor='w')
plot_group_of_districts(sitesMoreSierraLeone)

plt.show()
