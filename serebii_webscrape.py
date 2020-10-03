#! /usr/bin/python3
# serebii_webscrape.py
# mauduong

from datetime import datetime
from string import Formatter
from bs4 import BeautifulSoup
import json
import requests
import re

today = datetime.today().strftime('%Y%m%d%H%M%S')
OUTPUT_FILE = ('pokemon_scrape_%s.json' % today)

# TODO Generate an array for all pokemon in the galarian pokedex that is currently available
def getPokemon():
    pokemonList = []

    data = requests.get('https://www.serebii.net/swordshield/galarpokedex.shtml')
    page = data.content
    soup = BeautifulSoup(page, 'html.parser')

    try:
        pokemonName = soup.find_all('td', attrs={'align': 'center', 'class': 'fooinfo'})
        # pokemonHref = pokemonName.find('a')
    except Exception as ex:
        print('Beautiful Soup scraping pokemon array error')
        raise ex

    for td in pokemonName:
        # column = td.find_all('br')
        print(td)
        # pokemonList.append(pokemonName[2].text.replace('[^a-zA-Z]+', ''))
    # print(pokemonName)
    # print(pokemonList)

def getData(urlArray):
    try:
        pokemonDetailList = []

        for url in urlArray:
            data = requests.get(url);
            page = data.content
            soup = BeautifulSoup(page, 'html.parser')

            # Skip if pokemon not available
            if (data.status_code != "200"):
                break;

            try:
                pokemonHeader = soup.find_all('td', attrs={'class': 'fooinfo'})

                # Pokemon type
                pokemonTypeTd = soup.find('td', attrs={'class': 'cen'})
                pokemonTypeTr = pokemonTypeTd.find_all('tr')

                # Alternative forms e.g Normal, Alolan, Galarian
                pokemonTypeForm = {}
                pokemonTypes = []
                pokemonTypeList = []

                # TODO Fix the bullshit nested loop to properly display the correct form and type
                for form in pokemonTypeTr:
                    pokemonTypeForm['form'] = form.find_all('td')[0].text
                    for type in form.find_all('img', alt=True):
                        pokemonTypes.append(type.get('alt', '').replace('-type', '').lower())
                        pokemonTypeForm['type'] = pokemonTypes
                    # print(pokemonTypeForm)
                    pokemonTypes = []
                    pokemonTypeList.append(pokemonTypeForm)
                    print(pokemonTypeList)

                pokemonTypeImg = pokemonTypeTd.find_all('img')
                # TODO Weakness and Resistances based on the alternative forms and types
                # Weaknesses and Resistances
                # pokemonTypingTable = soup.find_all('table', attrs={'class': 'dextable', 'style': '@media (max-width:1011px) {display:none;}'})
                # pokemonTypingTr = pokemonTypingTable.find_all('tr')
                # pokemonTypingTd = pokemonTypingTable.find_next_siblings('td', attrs={'class': 'footype'})

                # Base stats
                serebiiLastTd = soup.find_all('td', attrs={'class': 'fooevo', 'colspan': '4'})[-1]

                # print('Scraping {0}'.format(pokemonHeader[1].text))
            except Exception as ex:
                print('Beautiful Soup scraping data error')
                raise ex

            # pokemonTypeList = []
            # for type in pokemonTypeImg:
            #     if type.get('alt', '').replace('-type', '').lower() not in pokemonTypeList:
            #         pokemonTypeList.append(type.get('alt', '').replace('-type', '').lower())

            pokemon = {}

            # Pokemon basic information
            pokemon['name'] = pokemonHeader[1].text
            pokemon['description'] = pokemonHeader[5].text
            pokemon['type'] = pokemonTypeList
            pokemon['ability'] = pokemonHeader[10].text.strip().replace(' (Available)', '').replace('\n', '')
            pokemon['height'] = pokemonHeader[6].text.strip().replace('\r\n\t\t\t', '\n')
            pokemon['weight'] = pokemonHeader[7].text.strip().replace('\r\n\t\t\t', '\n')
            pokemon['captureRate'] = pokemonHeader[8].text
            pokemon['stepsToHatchEgg'] = pokemonHeader[9].text

            # Pokemon typing weaknesses and resistances
            # pokemon['resistance'] = []
            # pokemon['weakness'] = []

            # Pokemon National, Galarian, Isle of Armor DLC Dex
            pokemonDexList = pokemonHeader[3].text
            pokemon['nationalNumber'] = re.search('[0-9]{3}|[-]{3}', pokemonDexList).group(0)
            pokemon['galarNumber'] = re.search('Galar: #[0-9]{3}|[-]{3}|[Foreign]{7}', pokemonDexList).group(0).replace('Foreign', '---').replace('Galar: #', '')
            pokemon['isleNumber'] = re.search('Isle of Armor: #[0-9]{3}|[-]{3}', pokemonDexList).group(0).replace('Isle of Armor: #', '')

            # TODO Fix base stats based on alternative forms
            # Hacky way to get pokemon base stats based on Gigantamax and multiple form
            try:
                # Gigantamax
                if 'Picture' in serebiiLastTd:
                    pokemonBaseStats = soup.find_all('table', {'class': 'dextable'})[-2].find_all('td', attrs={'align': 'center', 'class': 'fooinfo'})
                # Non-Gigantamax
                else:
                    pokemonBaseStats = soup.find_all('table', {'class': 'dextable'})[-1].find_all('td', attrs={'align': 'center', 'class': 'fooinfo'})
            except Exception as ex:
                print('Error caught getting base stats: {0}'.format(ex))
                raise ex

            # Pokemon Base Stats
            pokemon['hp'] = pokemonBaseStats[0].text
            pokemon['attack'] = pokemonBaseStats[1].text
            pokemon['defence'] = pokemonBaseStats[2].text
            pokemon['spattack'] = pokemonBaseStats[3].text
            pokemon['spdefence'] = pokemonBaseStats[4].text
            pokemon['speed'] = pokemonBaseStats[5].text

            # Pokemon Sword and Shield battle mechanic
            pokemon['dynamax'] = 'cannot' not in pokemonHeader[14].text
            pokemon['gigantamax'] = 'Gigantamax' in str(pokemonHeader[16])

            pokemonDetailList.append(pokemon)

        # print(pokemonDetailList)
        # saveData(pokemonDetailList)
    except Exception as ex:
        print('Error caught {0} for URL - {1}\n'.format(ex, url))
        raise ex

def saveData(pokemonList):
    with open(OUTPUT_FILE, 'a') as output_file:
        json.dump(pokemonList, output_file, indent = 2)

if __name__ == '__main__':
    try:
        # getPokemon()
        pokemonList = ['zacian'] #, 'slowpoke', 'zacian', 'venusaur'] #, 'thwackey', 'rillaboom'] #, 'zacian', 'zamazenta']
        urlList = ['https://www.serebii.net/pokedex-swsh/{}/'.format(pokemonList[p])
            for p in range(len(pokemonList))]

        getData(urlList)
    except Exception as ex:
        print('Error caught during main')
        raise ex