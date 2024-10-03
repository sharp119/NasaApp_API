from flask import Flask, jsonify, request, abort
import requests
from bs4 import BeautifulSoup
import logging

app = Flask(__name__)

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

def fetch_exoplanet_data(planet_name):
    url = f"https://www.exoplanetkyoto.org/exohtml/{planet_name}.html"
    headers = {
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8",
        "Accept-Language": "en-GB,en-US;q=0.9,en;q=0.8",        
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                      "AppleWebKit/537.36 (KHTML, like Gecko) "
                      "Chrome/124.0.0.0 Safari/537.36"    
    }
    try:
        response = requests.get(url, headers=headers, timeout=10)
        response.raise_for_status()
        return response.text
    except Exception as e:
        logging.error(f"An error occurred while fetching data for {planet_name}: {e}")
        return None

def parse_html(html_content):
    soup = BeautifulSoup(html_content, 'html.parser')
    data = {"Images": [], "Descriptive Lists": []}
    for img in soup.find_all('img'):
        data["Images"].append({"Description": img.get('alt', ''), "Source": img['src']})
    for li in soup.find_all('li'):
        if li.b:
            data["Descriptive Lists"].append(li.b.text.strip())
    return data

@app.route('/api/exoplanet', methods=['GET'])
def get_exoplanet_data():
    planet_name = request.args.get('planet_name')
    if not planet_name:
        abort(400, description="Please provide a planet name with the query parameter 'planet_name'.")
    
    logging.info(f"Fetching data for planet: {planet_name}")
    html_content = fetch_exoplanet_data(planet_name)
    if html_content:
        data = parse_html(html_content)
        return jsonify(data)
    else:
        abort(404, description=f"Data for {planet_name} could not be retrieved or does not exist.")

if __name__ == "__main__":
    app.run(debug=True)
