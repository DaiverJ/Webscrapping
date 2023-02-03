
import os
import re

import warnings
from datetime import date, datetime, timedelta


import numpy as np
import pandas as pd
import requests
from bs4 import BeautifulSoup


#Concatenate lists
def concatenate_list(lista, caracter):
    if isinstance(lista, list):
        if isinstance(caracter, str):
            return caracter.join(map(str, lista))
    raise TypeError('List parameter must be list')

#Drop emojis from text
def deEmojify(text):
    emoji_pattern = re.compile("["
                               u"\U0001F600-\U0001F64F"  # emoticons
                               u"\U0001F300-\U0001F5FF"  # symbols & pictographs
                               u"\U0001F680-\U0001F6FF"  # transport & map symbols
                               u"\U0001F1E0-\U0001F1FF"  # flags (iOS)
                               u"\U00002702-\U000027B0"
                               u"\U000024C2-\U0001F251"
                               u"\U0001f926-\U0001f937"
                               u"\U00010000-\U0010ffff"
                               "]+", flags=re.UNICODE)
    return emoji_pattern.sub(r'', text)


def ScrappEventbrite():
    print('Scraping de eventos iniciado')

    current_path = os.path.dirname(os.path.abspath(__file__))
    saving_path = f'{current_path}/webinars'

    url_first = 'https://www.eventbrite.co/d/online/free--'
    url_last = '--events--next-week/?lang=es&page='
    categories = ['business', 'science-and-tech']
    webinars = list()
    links = list()
    fecha = list()
    descripcion = list()
    descripcion1 = list()
    pages = np.arange(1, 11, 1)

    for category in categories:
        for page in pages:
            url = url_first + category + url_last
            url = url + str(page)
            print('Scrapeando {0}'.format(url))
            html_page = requests.get(url)
            soup = BeautifulSoup(html_page.content, 'html.parser')
            checkstate = soup.find_all('div', class_='empty-state__body')
            if checkstate == []:
                eventos = soup.find_all(
                    'div', class_='eds-event-card-content__primary-content')
                nombres = soup.find_all('div',
                                        class_='eds-event-card__formatted-name--is-clamped eds-event-card__formatted-name--is-clamped-three eds-text-weight--heavy')
                fechas = soup.find_all('div',
                                       class_='eds-event-card-content__sub-title eds-text-color--primary-brand eds-l-pad-bot-1 eds-l-pad-top-2 eds-text-weight--heavy eds-text-bm')
                
                for i in nombres:
                    webinars.append(deEmojify(i.text))
                for j in eventos:
                    links.append(j.a['href'])
                    urli = j.a['href']
                    pagei = requests.get(urli)
                    soupi = BeautifulSoup(pagei.content, 'html.parser')
                    try:
                        desceventos = soupi.find('div',
                                                 class_='structured-content-rich-text structured-content__module l-align-left l-mar-vert-6 l-sm-mar-vert-4 text-body-medium')
                        descripcion.append(desceventos.text)
                        resultado = concatenate_list(descripcion, '\n\n')
                        descripcion1.append(deEmojify(resultado))
                        for l in descripcion:
                            descripcion.remove(l)
                    except:
                        descripcion1.append('0')

                for k in fechas:
                    fecha.append(k.text)
            else:
                continue
            
    print('Scraping de eventos finalizado, creando excel')
    df = pd.DataFrame({'Titulo': webinars, 'Enlace': links,
                      'Descripción': descripcion1, 'Fechanf': fecha})
    df = df.drop_duplicates(subset=['Titulo'])
    df = df[df.Descripción != '0']
    df = df[df.Fechanf != '']
    df = df.reset_index()

    no_format_fechas = df['Fechanf'].tolist()
    format_fechas = []

    for fecha_nf in no_format_fechas:
        semifecha = fecha_nf[5:(fecha_nf.find('M ')+1)]
        zone = fecha_nf[fecha_nf.find('('):(fecha_nf.find(')')+1)]

        dt = datetime.strptime(semifecha, "%b %d, %Y %I:%M %p")
        if str(zone[1]) == '-':
            fecha_f = dt + \
                timedelta(
                    hours=int(zone[2:4])) + timedelta(minutes=int(zone[5:7])) - timedelta(hours=5)
        elif str(zone[1]) == '+':
            fecha_f = dt - \
                timedelta(
                    hours=int(zone[2:4])) - timedelta(minutes=int(zone[5:7])) - timedelta(hours=5)
        else:
            fecha_f = dt - timedelta(hours=5)
        format_fechas.append(fecha_f)

    df['Fecha'] = format_fechas
    df = df.drop(columns=['Fechanf', 'index'])

    dn = date.today()
    print(df)
    df.to_excel(os.path.join(
        saving_path, 'Webinars_{0}.xlsx'.format(dn)), index=False)
    print('Excel con eventos construido exitosamente')

if __name__ == '__main__':
    warnings.filterwarnings("ignore")
    ScrappEventbrite()