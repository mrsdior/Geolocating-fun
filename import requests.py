import requests
from urllib.parse import urlencode
from unicodedata import normalize
#Scope of this project was to automate searching for cemeteries across Romania, output in a txt file the name and coordinates like "X name; 45.xxxx, 41.xxxx"
#This is where I replaced "YOUR_API_KEY" with my Google Maps API key. I've signed up for GCP, and have used pretty much all of their map-related features. 
#Apparently, it isn't safe to put your actual API in this code, however, the only person to work on this code was me.
API_KEY = "YOUR_API_KEY"


# Function to read search queries from a text file given by me, with all possible cemeteries in all given places in Romania.
def get_queries(location_file):
    """
    Reads location names from a file (e.g., CSV), one per line.
    Returns a list of unique queries with diacritics removed.
    """
    queries = set()
    with open(location_file, "r") as f:
        for line in f:
            location = line.strip()
            if location:
                normalized_query = ''.join(c for c in normalize('NFD', location)
                                           if c in 'abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789 ')
                query = f"Cemetery in {normalized_query}"
                queries.add(query)
    return list(queries)


# Function to search for cemeteries
def search_cemeteries(query):
    """
    Uses Google Maps API to search for cemeteries near a location.
    Returns a list of dictionaries containing location data for found cemeteries.
    Prints a message if no results found or the API request fails.
    """
    params = {
        "key": API_KEY,
        "location": query,
        "radius": 5000,  # Reduced search radius to 5 km for better locality, I've tinkered with different radii, and 5 km seemed to be the sweet spot generally.
        "type": "cemetery",  # Specify type as cemetery
    }
    url = "https://maps.googleapis.com/maps/api/place/textsearch/json?" + urlencode(params)
    try:
        response = requests.get(url)
        data = response.json()
    except requests.exceptions.RequestException as e:
        print(f"Error: An error occurred while making the API request - {e}")
        return []  # Return empty list on error

    cemeteries = []
    if data["status"] == "OK":
        for result in data["results"]:
            cemetery = {
                "name": result["name"],
                "formatted_address": result["formatted_address"],
                "location": result["geometry"]["location"]
            }
            cemeteries.append(cemetery)
    else:
        print(f"No results found for cemeteries near: {query}")
    return cemeteries


# Main function
def main():
    """
    Reads location names from a file, searches for cemeteries across Romania, and writes results to a file.
    """
    location_file = "cemeteries.txt" 
    queries = get_queries(location_file)

    with open("Cemeteries.txt", "w", encoding="utf-8") as output_file: 
        for query in queries:
            output_file.write(f"Searching for cemeteries near: {query}\n")
            cemeteries = search_cemeteries(query)
            if cemeteries:
                for cemetery in cemeteries:
                    output_file.write(f"\t- {cemetery['name']}\n")
                    output_file.write(f"\t\tAddress: {cemetery['formatted_address']}\n")
                output_file.write("\n")
            else:
                output_file.write("No results found\n\n")


if __name__ == "__main__":
    main()

#First time I have tinkered with both GCP and Python, it was a fun little project! For the functionality I needed it, it isn't glamorous by any means. I just needed the raw output of location + coords.
#Do keep in mind, this isn't fully my code. I've found something online I could work with, and after that I just tinkered with it until it fit all my parameters.