import requests


def get_population_service(location: str, year: str = 2026):
    age2 = "20-24"
    age1 = "15-19"
    api1 = f"https://data.melbourne.vic.gov.au/api/explore/v2.1/catalog/datasets/city-of-melbourne-population-forecasts-by-small-area-2020-2040/records?limit=20&refine=geography%3A%22{location}%22&refine=age%3A%22Age%20{age1}%22&refine=year%3A%22{year}%22"
    api2 = f"https://data.melbourne.vic.gov.au/api/explore/v2.1/catalog/datasets/city-of-melbourne-population-forecasts-by-small-area-2020-2040/records?limit=20&refine=geography%3A%22{location}%22&refine=age%3A%22Age%20{age2}%22&refine=year%3A%22{year}%22"
    try:
        res1 = requests.get(api1).json()["results"]
        res2 = requests.get(api2).json()["results"]
        pop = sum(item["value"] for item in res1) + sum(item["value"] for item in res2)
        return {"population": pop, "location": location, "year": year}
    except Exception as e:
        return {"error": str(e)}
