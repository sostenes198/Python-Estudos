import requests
from bs4 import BeautifulSoup
from flask import Flask, jsonify, request
from flask_httpauth import HTTPBasicAuth
from flasgger import Swagger

app = Flask(__name__)

auth = HTTPBasicAuth()

users = {
    "user1": "password1",
    "user2": "password2"
}

app.config["SWAGGER"] = {
    'title': 'Flask API',
    'universion': 3
}

swagger = Swagger(app)


@auth.verify_password
def verify_password(username, password):
    if username in users and users[username] == password:
        return username

    return None


def get_title(url):
    try:
        response = requests.get(url)
        soup = BeautifulSoup(response.text, 'html.parser')
        title = soup.title.strip()
        return jsonify({"title": title})
    except Exception as e:
        return jsonify({"error": str(e)}), 500


def get_content(url):
    try:
        response = requests.get(url)
        soup = BeautifulSoup(response.text, 'html.parser')
        headers = []

        for header_tag in ['h1', 'h2', 'h3']:
            for header in soup.findAll(header_tag):
                headers.append(header.get_text(strip=True))

        paragraphs = [p.get_text(strip=True) for p in soup.findAll('p')]

        return jsonify({"headers": headers, "paragraphs": paragraphs})
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route('/')
@auth.login_required
def home():
    return '<h1>Hello World!</h1>'


items = []


@app.route('/items', methods=['GET'])
def get_items():
    return jsonify(items)


@app.route('/items', methods=['POST'])
def create_item():
    data = request.get_json()
    items.append(data)
    return jsonify(items), 201


@app.route('/items/<int:item_id>', methods=['PUT'])
def update_item(item_id):
    data = request.get_json()
    index = next((i for i, u in enumerate(items) if u["id"] == item_id), None)
    if index is not None:
        items[index].update(data)
        return jsonify(items[index]), 200

    return jsonify({"error": "Item not found"}), 404


@app.route('/items/<int:item_id>', methods=['DELETE'])
def delete_item(item_id):
    index = next((i for i, u in enumerate(items) if u["id"] == item_id), None)
    if index is not None:
        item = items[index]
        items.pop(index)
        return jsonify(item), 200

    return jsonify({"error": "Item not found"}), 404


@app.route('/scrape/title', methods=['GET'])
@auth.login_required
def scrape_title():
    url = request.args.get('url')
    if not url:
        return jsonify({"error": "URL required"}), 400

    return get_title(url)


@app.route('/scrape/content', methods=['GET'])
@auth.login_required
def scrape_content():
    url = request.args.get('url')
    if not url:
        return jsonify({"error": "URL required"}), 400

    return get_content(url)


if __name__ == '__main__':
    app.run(debug=True)
