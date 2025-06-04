"""
This module implements a simple Flask API for managing items.
It provides endpoints for retrieving, adding, updating, and deleting items.
"""
from flask import Flask, jsonify, request, abort

# Initialize the Flask application
app = Flask(__name__)

# In a real application, you'd use a database.
# For this example, we'll use a simple in-memory list to store items.
items = [
    {'id': 1, 'name': 'Laptop', 'price': 1200},
    {'id': 2, 'name': 'Mouse', 'price': 25},
    {'id': 3, 'name': 'Keyboard', 'price': 75}
]
# Using a leading underscore to indicate this is an internal, mutable module-level variable
_next_id = 4 # Simple way to generate unique IDs for new items

@app.route('/api/items', methods=['GET'])
def get_all_items():
    """
    Handles GET requests to retrieve all items.
    Returns:
        A JSON array of all available items.
    """
    return jsonify(items)

@app.route('/api/items/<int:item_id>', methods=['GET'])
def get_item_by_id(item_id):
    """
    Handles GET requests to retrieve a single item by its ID.
    Args:
        item_id (int): The ID of the item to retrieve.
    Returns:
        A JSON object of the requested item if found, otherwise an error message.
    """
    item = next((item for item in items if item['id'] == item_id), None)
    if item:
        return jsonify(item)
    # If item not found, return a 404 Not Found error.
    # Removed unnecessary 'else' block as the function returns if 'item' is found.
    abort(404, description=f"Item with ID {item_id} not found.")

@app.route('/api/items', methods=['POST'])
def add_item():
    """
    Handles POST requests to add a new item.
    Expects a JSON body with 'name' and 'price' fields.
    Returns:
        A JSON object confirming the item addition, or an error message.
    """
    # Check if the request body is JSON
    if not request.is_json:
        abort(400, description="Request must be JSON.")

    data = request.json

    # Validate required fields
    if 'name' not in data or 'price' not in data:
        abort(400, description="Missing 'name' or 'price' in request body.")

    # Validate data types
    if not isinstance(data['name'], str) or not isinstance(data['price'], (int, float)):
        abort(400, description="'name' must be a string and 'price' must be a number.")

    # Pylint warns about 'global' statement. In a real app, this data would be
    # managed by a database layer or an object-oriented approach to avoid global state.
    global _next_id
    new_item = {
        'id': _next_id,
        'name': data['name'],
        'price': data['price']
    }
    items.append(new_item)
    _next_id += 1 # Increment for the next new item

    # Return 201 Created status code for successful creation
    return jsonify({'message': 'Item added successfully', 'item': new_item}), 201

@app.route('/api/items/<int:item_id>', methods=['PUT'])
def update_item(item_id):
    """
    Handles PUT requests to update an existing item by its ID.
    Expects a JSON body with 'name' and/or 'price' fields.
    Returns:
        A JSON object confirming the update, or an error message.
    """
    item = next((item for item in items if item['id'] == item_id), None)
    if not item:
        abort(404, description=f"Item with ID {item_id} not found.")

    if not request.is_json:
        abort(400, description="Request must be JSON.")

    data = request.json

    # Update fields if provided and valid
    if 'name' in data:
        if not isinstance(data['name'], str):
            abort(400, description="'name' must be a string.")
        item['name'] = data['name']
    if 'price' in data:
        if not isinstance(data['price'], (int, float)):
            abort(400, description="'price' must be a number.")
        item['price'] = data['price']

    # If no valid fields were provided for update
    if not data:
        abort(400, description="No update data provided.")

    return jsonify({'message': 'Item updated successfully', 'item': item})

@app.route('/api/items/<int:item_id>', methods=['DELETE'])
def delete_item(item_id):
    """
    Handles DELETE requests to remove an item by its ID.
    Returns:
        A JSON object confirming the deletion, or an error message.
    """
    # Pylint warns about 'global' statement. See comment in add_item.
    global items
    # Filter out the item to be deleted
    initial_length = len(items)
    items = [item for item in items if item['id'] != item_id]

    if len(items) == initial_length:
        # If length didn't change, item was not found
        abort(404, description=f"Item with ID {item_id} not found.")
    else:
        return jsonify({'message': f'Item with ID {item_id} deleted successfully'}), 200 # OK status

# Global error handler for 400 Bad Request
@app.errorhandler(400)
def bad_request(_error): # Renamed 'error' to '_error' to mark as intentionally unused
    """Handles 400 Bad Request errors."""
    return jsonify({'error': 'Bad Request', 'message': _error.description}), 400

# Global error handler for 404 Not Found
@app.errorhandler(404)
def not_found(_error): # Renamed 'error' to '_error'
    """Handles 404 Not Found errors."""
    return jsonify({'error': 'Not Found', 'message': _error.description}), 404

# Global error handler for 405 Method Not Allowed
@app.errorhandler(405)
def method_not_allowed(_error): # Renamed 'error' to '_error'
    """Handles 405 Method Not Allowed errors."""
    return jsonify({'error': 'Method Not Allowed', 'message': _error.description}), 405

# Global error handler for 500 Internal Server Error (for unexpected errors)
@app.errorhandler(500)
def internal_server_error(_error): # Renamed 'error' to '_error'
    """
    Handles 500 Internal Server Errors.
    In a production environment, you might log the actual error here.
    """
    # Shortened message to fit line length.
    return jsonify({'error': 'Internal Server Error',
                    'message': 'An unexpected error occurred.'}), 500


if __name__ == '__main__':
    # Run the Flask development server.
    # debug=True enables auto-reloading on code changes and provides a debugger.
    app.run(debug=True)