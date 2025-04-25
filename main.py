from fastapi import FastAPI

import aiohttp
from bs4 import BeautifulSoup
from fake_useragent import UserAgent

import asyncio

class RealtimeScraper:
    def __init__(self):
        self.session = None
        self.ua = UserAgent()
    

    async def initializeSession(self):
        self.session = aiohttp.ClientSession()
        self.session.headers.update(
            {
                "User-Agent": self.ua.random,
                "Host": "markets.businessinsider.com"
            }
        )

    # main scraper
    async def scrape(self):
        data = []
        response = await self.session.get('https://markets.businessinsider.com/commodities')

        if response.status != 200:
            return {'error': f'response returned {response.status}, please contact the developer.'}
        
        soup = BeautifulSoup(await response.read(), 'html.parser')

        # find all objects
        commodities = soup.find_all('tr', class_='table__tr')

        # extract their data
        for i in commodities:
            name = i.find('td', class_='table__td bold')
            price = i.find('div', {'data-field': 'Mid'})
            percentage = i.find('div', {'data-field': 'ChangePer'})
            abss = i.find('div', {'data-field': 'ChangeAbs'})
            unit = i.find('td', class_='table__td text-right')
            date = i.find('div', {'data-field': 'MidTimestamp'})

            if not name:
                continue

            data.append(
                {
                    "name": name.text,
                    "price": price.text,
                    "percentage": percentage.text,
                    "abss": abss.text,
                    "unit": unit.text,
                    "date": date.text
                }
            )
        
        return data

app = FastAPI()

first = True
rs = RealtimeScraper()

@app.get("/")
async def main():
    global first

    if first:
        await rs.initializeSession()
        first = False

    data = await rs.scrape()

    return data
