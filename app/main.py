from app.nearby_restaurants import run_simple_demo
from app.nearby_interest import fetch_nearby_interest
import requests
from fastapi import FastAPI
from pydantic import BaseModel

if __name__ == "__main__":
    run_simple_demo()

app = FastAPI()
class InterestQuery(BaseModel):
    query: str #
    location: str #should be at city level, If several locations match the location requested, we'll pick the most popular one. 


@app.post("/api/nearby-interest")
def get_nearby_interest(data: InterestQuery):
    try:
        res = fetch_nearby_interest(data.query, data.location)
        return res
    except Exception as e:
        return {"error": str(e)}