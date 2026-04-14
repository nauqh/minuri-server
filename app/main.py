from app.nearby_interest import fetch_nearby_interest
import requests
from fastapi import FastAPI
from pydantic import BaseModel



app = FastAPI()

#getting a list of nearby interest based on the query and location.
@app.get("/api/nearby-interest")
async def get_nearby_interest(query: str, location: str="Melbourne"):
    try:
        res = fetch_nearby_interest(query, location)
        return res
    except Exception as e:
        return {"error": str(e)}
    
#getting population of certain suburb and year, then sum up the population of age group 15-19 and 20-24 as the final result.
@app.get("/api/population")
#https://data.melbourne.vic.gov.au/api/explore/v2.1/catalog/datasets/city-of-melbourne-population-forecasts-by-small-area-2020-2040/records?limit=20&refine=geography%3A%22Carlton%22&refine=age%3A%22Age%2020-24%22&refine=year%3A%222026%22
#getting pop of age group 15-19 and 20-24 of certain suburb and year, then sum them up as the final result.
async def get_population(location: str, year: str= 2026):
    age2 = "20-24"
    age1 = "15-19"
    api1 = f"https://data.melbourne.vic.gov.au/api/explore/v2.1/catalog/datasets/city-of-melbourne-population-forecasts-by-small-area-2020-2040/records?limit=20&refine=geography%3A%22{location}%22&refine=age%3A%22Age%20{age1}%22&refine=year%3A%22{year}%22"
    api2 = f"https://data.melbourne.vic.gov.au/api/explore/v2.1/catalog/datasets/city-of-melbourne-population-forecasts-by-small-area-2020-2040/records?limit=20&refine=geography%3A%22{location}%22&refine=age%3A%22Age%20{age2}%22&refine=year%3A%22{year}%22"
    try:
        res1 = requests.get(api1).json()["results"]
        res2 = requests.get(api2).json()["results"]
        pop = sum(item['value'] for item in res1) + sum(item['value'] for item in res2)
        return {"population": pop, "location": location, "year": year}
    except Exception as e:
        return {"error": str(e)}
    
#getting a list of possible suburbs in 2026, which is based on the population forecast data of 2026 of the city of melbourne.
@app.get("/api/get-Suburb")
def get_suburb():
    '''
    Possible suburbs 2026:
    Carlton
    City of Melbourne
    Docklands
    East Melbourne
    Kensington
    Melbourne (CBD)
    Melbourne (Remainder)
    North Melbourne
    Parkville
    Port Melbourne
    South Yarra
    Southbank
    West Melbourne (Industrial)
    West Melbourne (Residential)
    '''
    try:
        suburbs = ["Carlton", "City of Melbourne", "Docklands", "East Melbourne", "Kensington", "Melbourne (CBD)", "Melbourne (Remainder)", "North Melbourne", "Parkville", "Port Melbourne", "South Yarra", "Southbank", "West Melbourne (Industrial)", "West Melbourne (Residential)"]
        return {"suburbs": suburbs}
    except Exception as e:
        return {"error": str(e)}