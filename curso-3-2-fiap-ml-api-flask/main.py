from flask import Flask, jsonify, request

app = Flask(__name__)


@app.route('/')
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

if __name__ == '__main__':
    app.run(debug=True)
