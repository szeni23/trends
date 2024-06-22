import httpx
import json
import pandas as pd
from datetime import datetime

today = datetime.today().strftime('%Y%m%d')

start_date_str = today 
end_date_str = today 

start_date = datetime.strptime(start_date_str, '%Y%m%d')
end_date = datetime.strptime(end_date_str, '%Y%m%d')

# Load your DataFrame with the list of countries
df_countries = pd.read_csv("countries.csv")

result = []

# Iterate through each country in the DataFrame
for geo_location in df_countries['country']:
    # Decrement the date parameter to get trends data of previous days
    for day in range(start_date, end_date - 1, -1):

        url = f"https://trends.google.com/trends/api/dailytrends?hl=en-{geo_location}&tz=-180&ed={day}&geo={geo_location}&hl=en-US&ns=15"

        response = httpx.get(url=url)

        if response.status_code == 200 and response.text.strip():
            try:
                data = json.loads(response.text.replace(")]}',", ""))
            except json.JSONDecodeError:
                print(f"Failed to decode JSON for date: {day} in country: {geo_location}")
                continue

            # Check if the list is not empty before accessing its elements
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
                print(f"No data available for the date: {day} in country: {geo_location}")
        else:
            print(f"Failed to retrieve data for date: {day} in country: {geo_location}")
            print(f"Response status code: {response.status_code}")
            print(f"Response text: {response.text.strip()}")

# Create a DataFrame from the result list
df_trends = pd.DataFrame(result)

# Save the DataFrame to a CSV file
df_trends.to_csv("trends.csv", index=False)

print("Trends data has been saved to trends.csv")
