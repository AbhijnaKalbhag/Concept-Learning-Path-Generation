from flask import Flask, request, jsonify, render_template

import requests

from bs4 import BeautifulSoup

import json

app = Flask(__name__)

from pymongo import MongoClient



# MongoDB Connection String

ATLAS_URI = "mongodb+srv://root:root@cluster0.22drow0.mongodb.net/?retryWrites=true&w=majority"

# Function to get prerequisites using 'What links here' API

def get_prerequisites(concept):

    url = f"https://en.wikipedia.org/w/api.php?action=query&titles={concept.replace(' ', '_')}&prop=linkshere&lhnamespace=0&format=json"

    response = requests.get(url, headers={'User-Agent': 'MyWikipediaBot/1.0'})

    

    prerequisites = []

    if response.status_code == 200:

        data = response.json()

        page_id = list(data['query']['pages'].keys())[0]

        if 'linkshere' in data['query']['pages'][page_id]:

            for link in data['query']['pages'][page_id]['linkshere']:

                prerequisites.append(link['title'])

    return prerequisites



# Function to get concepts (links) from the current Wikipedia page

def get_concepts_from_page(concept):

    url = f"https://en.wikipedia.org/wiki/{concept.replace(' ', '_')}"

    response = requests.get(url, headers={'User-Agent': 'MyWikipediaBot/1.0'})

    

    concepts = []

    if response.status_code == 200:

        soup = BeautifulSoup(response.text, 'html.parser')

        content_div = soup.find('div', {'class': 'mw-parser-output'})

        

        if content_div:

            paragraphs = content_div.find_all('p')

            for p in paragraphs[:15]:  # Limiting to the first 15 <p> elements

                hyperlinks = p.find_all('a', href=True)

                for link in hyperlinks:

                    href = link['href']

                    if not href.startswith('#cite_note'):  # Exclude citation links

                        concept_name = link.get_text().strip()

                        if concept_name:

                            concepts.append(concept_name)

    return concepts



# Function to get 'See also' section (advanced topics)

def get_advanced_concepts(concept):

    url = f'https://en.wikipedia.org/wiki/{concept.replace(" ", "_")}'

    response = requests.get(url, headers={'User-Agent': 'MyWikipediaBot/1.0'})

    

    advanced_topics = []

    if response.status_code == 200:

        soup = BeautifulSoup(response.text, 'html.parser')

        see_also_section = soup.find('span', {'id': 'See_also'})

        

        if see_also_section:

            advanced_list = see_also_section.find_next('ul')

            if advanced_list:

                for li in advanced_list.find_all('li'):

                    advanced_topics.append(li.get_text().strip())

    return advanced_topics



# Function to generate a text-based learning path

def generate_learning_path1(concept):

    prerequisites = get_prerequisites(concept)

    current_concepts = get_concepts_from_page(concept)

    advanced_concepts = get_advanced_concepts(concept)



    # Generate the learning path as a text

    path = " -> ".join(prerequisites + [concept] + current_concepts[:15] + advanced_concepts)

    return path





# Function to store data in MongoDB

def generate_learning_path(concept):

    # Retrieve prerequisites, current concepts, and advanced concepts

    prerequisites = get_prerequisites(concept)

    current_concepts = get_concepts_from_page(concept)

    advanced_concepts = get_advanced_concepts(concept)



    # Prepare data as a dictionary

    learning_path_data = {

        "concept": concept,

        "prerequisites": prerequisites,

        "current_concepts": current_concepts[:15],  # Limit to first 15

        "advanced_concepts": advanced_concepts

    }



    # Connect to MongoDB

    client = MongoClient(ATLAS_URI)

    db = client["learningpath"]  # Database name

    collection = db["wiki"]      # Collection name



    # Insert data into MongoDB

    result = collection.insert_one(learning_path_data)

    print(f"Data for '{concept}' stored in MongoDB with ID: {result.inserted_id}")



    # Return a path as a string

    path = " -> ".join(prerequisites + [concept] + current_concepts[:15] + advanced_concepts)

    return path





def generate_learning_path2(concept):

    # Retrieve prerequisites, current concepts, and advanced concepts

    prerequisites = get_prerequisites(concept)

    current_concepts = get_concepts_from_page(concept)

    advanced_concepts = get_advanced_concepts(concept)



    # Prepare data as a dictionary

    learning_path_data = {

        "concept": concept,

        "prerequisites": prerequisites,

        "current_concepts": current_concepts[:15],  # Limit to first 15

        "advanced_concepts": advanced_concepts

    }



    # Save the data into a JSON file

    with open(f"{concept}_learning_path.json", "w", encoding="utf-8") as json_file:

        json.dump(learning_path_data, json_file, indent=4, ensure_ascii=False)



    print(f"Learning path data for '{concept}' has been saved to '{concept}_learning_path.json'.")



    path = " -> ".join(prerequisites + [concept] + current_concepts[:15] + advanced_concepts)

    return path



# Flask route to render the home page

@app.route("/")

def home():

    return render_template("index.html")



# Flask route to handle the learning path request

@app.route("/generate", methods=["POST"])

def generate():

    data = request.get_json()  # Fetch JSON data from the request

    concept = data.get("concept")  # Extract the 'concept' field

    if not concept:

        return jsonify({"error": "Concept is required"}), 400



    path = generate_learning_path(concept)

    return jsonify({"path": path})



# Flask route for testing

@app.route("/test")

def test():

    return jsonify({"message": "Flask app is working!"})



# Run the Flask app

if __name__ == "__main__":

    app.run(debug=True, port=3000)

