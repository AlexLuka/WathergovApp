import requests


res = requests.get("https://api.weather.gov")


print(res.content)
