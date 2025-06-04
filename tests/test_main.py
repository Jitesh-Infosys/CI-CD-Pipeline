import unittest
import json
# Import the app.main module itself so we can access its global variables directly
import app.main

class FlaskApiTestCase(unittest.TestCase):
    """
    Test suite for the Flask API endpoints.
    """

    def setUp(self):
        """
        Set up the test client and initialize the in-memory data before each test.
        This ensures tests are isolated and start with a clean state.
        """
        # Access the Flask app instance directly from the imported module
        self.client = app.main.app.test_client()
        app.main.app.testing = True # Enable testing mode for Flask app

        # Reset the in-memory data directly by modifying the global variables
        # within the app.main module. This is crucial for test isolation.
        app.main.items.clear() # Clear the existing list in app.main
        app.main.items.extend([ # Populate it with the initial test data
            {'id': 1, 'name': 'Laptop', 'price': 1200},
            {'id': 2, 'name': 'Mouse', 'price': 25},
            {'id': 3, 'name': 'Keyboard', 'price': 75}
        ])
        app.main._next_id = 4 # Reset the next_id in app.main

    def test_get_all_items(self):
        """
        Test the GET /api/items endpoint to retrieve all items.
        """
        response = self.client.get('/api/items')
        self.assertEqual(response.status_code, 200)
        # Assert against the known initial state, which setUp ensures is consistent
        self.assertEqual(json.loads(response.data), [
            {'id': 1, 'name': 'Laptop', 'price': 1200},
            {'id': 2, 'name': 'Mouse', 'price': 25},
            {'id': 3, 'name': 'Keyboard', 'price': 75}
        ])

    def test_get_item_by_id_success(self):
        """
        Test the GET /api/items/<id> endpoint for a successful retrieval.
        """
        response = self.client.get('/api/items/1')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(json.loads(response.data), {'id': 1, 'name': 'Laptop', 'price': 1200})

    def test_get_item_by_id_not_found(self):
        """
        Test the GET /api/items/<id> endpoint for a non-existent item.
        Expects a 404 Not Found error.
        """
        response = self.client.get('/api/items/999')
        self.assertEqual(response.status_code, 404)
        self.assertIn(b"Item with ID 999 not found.", response.data)

    def test_add_item_success(self):
        """
        Test the POST /api/items endpoint for successful item creation.
        """
        new_item_data = {'name': 'Monitor', 'price': 300}
        response = self.client.post(
            '/api/items',
            data=json.dumps(new_item_data),
            content_type='application/json'
        )
        self.assertEqual(response.status_code, 201) # 201 Created
        response_data = json.loads(response.data)
        self.assertIn('message', response_data)
        self.assertIn('item', response_data)
        self.assertEqual(response_data['item']['name'], 'Monitor')
        self.assertEqual(response_data['item']['price'], 300)
        self.assertEqual(response_data['item']['id'], 4) # Expecting the next_id

        # Verify the item was actually added by fetching all items from the API
        get_response = self.client.get('/api/items')
        current_items = json.loads(get_response.data)
        self.assertEqual(len(current_items), 4) # This assertion should now pass
        self.assertEqual(current_items[3]['name'], 'Monitor')
        self.assertEqual(current_items[3]['id'], 4)

    def test_add_item_missing_name(self):
        """
        Test POST /api/items with missing 'name' field.
        Expects a 400 Bad Request error.
        """
        invalid_data = {'price': 50}
        response = self.client.post(
            '/api/items',
            data=json.dumps(invalid_data),
            content_type='application/json'
        )
        self.assertEqual(response.status_code, 400)
        self.assertIn(b"Missing 'name' or 'price' in request body.", response.data)

    def test_add_item_invalid_price_type(self):
        """
        Test POST /api/items with invalid 'price' type.
        Expects a 400 Bad Request error.
        """
        invalid_data = {'name': 'Charger', 'price': 'fifty'}
        response = self.client.post(
            '/api/items',
            data=json.dumps(invalid_data),
            content_type='application/json'
        )
        self.assertEqual(response.status_code, 400)
        self.assertIn(b"'name' must be a string and 'price' must be a number.", response.data)

    def test_add_item_non_json_request(self):
        """
        Test POST /api/items with a non-JSON request body.
        Expects a 400 Bad Request error.
        """
        response = self.client.post(
            '/api/items',
            data="This is not JSON",
            content_type='text/plain' # Incorrect content type
        )
        self.assertEqual(response.status_code, 400)
        self.assertIn(b"Request must be JSON.", response.data)

    def test_update_item_success(self):
        """
        Test the PUT /api/items/<id> endpoint for successful item update.
        """
        update_data = {'price': 1300}
        response = self.client.put(
            '/api/items/1',
            data=json.dumps(update_data),
            content_type='application/json'
        )
        self.assertEqual(response.status_code, 200)
        response_data = json.loads(response.data)
        self.assertIn('message', response_data)
        self.assertIn('item', response_data)
        self.assertEqual(response_data['item']['id'], 1)
        self.assertEqual(response_data['item']['price'], 1300)

        # Verify the item was actually updated by fetching it again from the API
        get_response = self.client.get('/api/items/1')
        updated_item = json.loads(get_response.data)
        self.assertEqual(updated_item['price'], 1300) # This assertion should now pass

    def test_update_item_not_found(self):
        """
        Test PUT /api/items/<id> for a non-existent item.
        Expects a 404 Not Found error.
        """
        update_data = {'price': 500}
        response = self.client.put(
            '/api/items/999',
            data=json.dumps(update_data),
            content_type='application/json'
        )
        self.assertEqual(response.status_code, 404)
        self.assertIn(b"Item with ID 999 not found.", response.data)

    def test_update_item_no_data(self):
        """
        Test PUT /api/items/<id> with an empty JSON body.
        Expects a 400 Bad Request error.
        """
        response = self.client.put(
            '/api/items/1',
            data=json.dumps({}),
            content_type='application/json'
        )
        self.assertEqual(response.status_code, 400)
        self.assertIn(b"No update data provided.", response.data)

    def test_delete_item_success(self):
        """
        Test the DELETE /api/items/<id> endpoint for successful item deletion.
        """
        response = self.client.delete('/api/items/2')
        self.assertEqual(response.status_code, 200)
        self.assertIn(b"Item with ID 2 deleted successfully", response.data)

        # Verify the item was actually removed by fetching all items from the API
        get_response = self.client.get('/api/items')
        current_items = json.loads(get_response.data)
        self.assertEqual(len(current_items), 2) # This assertion should now pass
        self.assertNotIn({'id': 2, 'name': 'Mouse', 'price': 25}, current_items)
        self.assertEqual(current_items, [
            {'id': 1, 'name': 'Laptop', 'price': 1200},
            {'id': 3, 'name': 'Keyboard', 'price': 75}
        ])

    def test_delete_item_not_found(self):
        """
        Test DELETE /api/items/<id> for a non-existent item.
        Expects a 404 Not Found error.
        """
        response = self.client.delete('/api/items/999')
        self.assertEqual(response.status_code, 404)
        self.assertIn(b"Item with ID 999 not found.", response.data)

    def test_method_not_allowed(self):
        """
        Test an invalid HTTP method for an endpoint.
        Expects a 405 Method Not Allowed error.
        """
        response = self.client.post('/api/items/1') # POST not allowed on /api/items/<id>
        self.assertEqual(response.status_code, 405)
        self.assertIn(b"Method Not Allowed", response.data)


if __name__ == '__main__':
    unittest.main()

