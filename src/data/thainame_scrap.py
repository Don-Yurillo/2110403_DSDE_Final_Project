import requests
import re
from bs4 import BeautifulSoup
import pandas as pd

startpage = 1
endpage = 13

namelist = []

for i in range(startpage, endpage+1):
    data = requests.get('https://www.behindthename.com/submit/names/usage/thai/'+str(i))
    soup = BeautifulSoup(data.text, 'html.parser')
    # names = soup.find_all('span',class_='listname')
    # for name in names:
    #     print(name.text)
    #     namelist.append(name.text)
    browses = soup.find_all('div',class_='browsename')
    for browse in browses:
        name = browse.find('span',class_='listname')   
        gender = browse.find('span',class_='listgender')
        if '&' in gender.text :
            namelist.append((name.text,'m'))
            namelist.append((name.text,'f'))
        else:
            namelist.append((name.text,gender.text))
        
df = pd.DataFrame(namelist, columns=['name','gender'])
df.to_csv('thainamelist.csv')