from app.nearby_interest import fetch_nearby_interest
import requests
from fastapi import FastAPI
from pydantic import BaseModel



app = FastAPI()
#used for getting nearby interest details from SerpApi Google Local results. 
class InterestQuery(BaseModel):
    query: str #
    location: str #should be at city level, If several locations match the location requested, we'll pick the most popular one. 
#used for getting population data from https://data.melbourne.vic.gov.au/ (City of melbourne opendata)
class populationQuery(BaseModel):
    location:str#Suburb name, e.g. "Carlton" should start with capital letter
    year:str

@app.post("/api/nearby-interest")
def get_nearby_interest(data: InterestQuery):
    try:
        res = fetch_nearby_interest(data.query, data.location)
        return res
    except Exception as e:
        return {"error": str(e)}

@app.post("/api/population")
#https://data.melbourne.vic.gov.au/api/explore/v2.1/catalog/datasets/city-of-melbourne-population-forecasts-by-small-area-2020-2040/records?limit=20&refine=geography%3A%22Carlton%22&refine=age%3A%22Age%2020-24%22&refine=year%3A%222026%22
#getting pop of age group 15-19 and 20-24 of certain suburb and year, then sum them up as the final result.
def get_population(data: populationQuery):
    age2 = "20-24"
    age1 = "15-19"
    api1 = f"https://data.melbourne.vic.gov.au/api/explore/v2.1/catalog/datasets/city-of-melbourne-population-forecasts-by-small-area-2020-2040/records?limit=20&refine=geography%3A%22{data.location}%22&refine=age%3A%22Age%20{age1}%22&refine=year%3A%22{data.year}%22"
    api2 = f"https://data.melbourne.vic.gov.au/api/explore/v2.1/catalog/datasets/city-of-melbourne-population-forecasts-by-small-area-2020-2040/records?limit=20&refine=geography%3A%22{data.location}%22&refine=age%3A%22Age%20{age2}%22&refine=year%3A%22{data.year}%22"
    try:
        res1 = requests.get(api1).json()["results"]
        res2 = requests.get(api2).json()["results"]
        pop = sum(item['value'] for item in res1) + sum(item['value'] for item in res2)
        return {"population": pop, "location": data.location, "year": data.year}
    except Exception as e:
        return {"error": str(e)}

@app.get("/api/get-Suburb")
def get_suburb():
    try:
        pass
    except Exception as e:
        return {"error": str(e)}