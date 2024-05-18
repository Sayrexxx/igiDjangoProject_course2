import requests
import tmdbsimple as tmdb
from django.shortcuts import render
import random
import logging

logging.basicConfig(level=logging.INFO, filename='logs.log', filemode='a',
                    format='%(asctime)s %(levelname)s %(message)s')

def cats(request):
    page = random.randint(1, 34)
    response = requests.get(f'https://catfact.ninja/facts?page={page}')
    response = response.json()
    logging.info("Get response successfully")
    data = response['data']
    facts = list()
    for i in range(len(data)):
        facts.append(data[i]["fact"])
    return render(request, 'cat_facts.html', {"facts": facts})

def random_joke(request):
    url = 'https://official-joke-api.appspot.com/random_joke'
    response = requests.get(url)

    if response.status_code == 200:
        try:
            joke = response.json()
            logging.info("Got response successfully")
            data = {
                'setup': joke.get('setup', 'No setup available'),
                'punchline': joke.get('punchline', 'No punchline available')
            }
        except ValueError:
            logging.error("Error parsing JSON response")
            data = {
                'setup': "Sorry, we couldn't fetch a joke at this time.",
                'punchline': ""
            }
    else:
        logging.error("Failed to get response from the joke API")
        data = {
            'setup': "Sorry, we couldn't fetch a joke at this time.",
            'punchline': ""
        }

    return render(request, 'random_joke.html', {"joke": data})