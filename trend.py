import httpx
import json
import pandas as pd
from datetime import datetime, timedelta

today = datetime.today().strftime('%Y%m%d')

start_date_str = today 
end_date_str = today 

start_date = datetime.strptime(start_date_str, '%Y%m%d')
end_date = datetime.strptime(end_date_str, '%Y%m%d')

df_countries = pd.read_csv("countries.csv")

result = []

for geo_location in df_countries['country']:
    current_date = start_date
    while current_date >= end_date:
        day_str = current_date.strftime('%Y%m%d')

        url = f"https://trends.google.com/trends/api/dailytrends?hl=en-{geo_location}&tz=-180&ed={day_str}&geo={geo_location}&hl=en-US&ns=15"

        response = httpx.get(url=url)

        if response.status_code == 200 and response.text.strip():
            try:
                data = json.loads(response.text.replace(")]}',", ""))
            except json.JSONDecodeError:
                print(f"Failed to decode JSON for date: {day_str} in country: {geo_location}")
                current_date -= timedelta(days=1)
                continue

            if data["default"]["trendingSearchesDays"]:
                date = data["default"]["trendingSearchesDays"][0]["formattedDate"]
                for trend in data["default"]["trendingSearchesDays"][0]["trendingSearches"]:
                    trend_object = {
                        "Title": trend["title"]["query"],
                        "Traffic volume": trend["formattedTraffic"],
                        "Link": "https://trends.google.com/" + trend["title"]["exploreLink"],
                        "Date": date,
                        "Geo Location": geo_location
                    }
                    result.append(trend_object)
            else:
                print(f"No data available for the date: {day_str} in country: {geo_location}")
        else:
            print(f"Failed to retrieve data for date: {day_str} in country: {geo_location}")
            print(f"Response status code: {response.status_code}")
            print(f"Response text: {response.text.strip()}")

        current_date -= timedelta(days=1)

df_trends = pd.DataFrame(result)

df_trends.to_csv("trends.csv", index=False)

print("Trends data has been saved to trends.csv")
