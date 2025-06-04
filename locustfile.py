"""
This module defines Locust user behavior for load testing the Flask API.
It simulates various interactions like fetching, adding, and updating items.
"""
import random  # Standard library imports first
import json    # For JSONDecodeError
from locust import HttpUser, task, between # Third-party imports after standard ones

class WebsiteUser(HttpUser):
    """
    Simulates a user interacting with the Flask API.
    """
    # Host of the API. Make sure your Flask app is running on this address.
    host = "http://127.0.0.1:5000"

    # Wait time between consecutive tasks for a user
    # Users will wait between 1 and 2 seconds between performing tasks.
    wait_time = between(1, 2)

    # A list of initial items, similar to your app.py's in-memory store
    # This helps in simulating realistic GET requests for existing items
    initial_items = [
        {'id': 1, 'name': 'Laptop', 'price': 1200},
        {'id': 2, 'name': 'Mouse', 'price': 25},
        {'id': 3, 'name': 'Keyboard', 'price': 75}
    ]
    # We'll keep track of IDs to try and GET or PUT/DELETE for
    known_item_ids = [item['id'] for item in initial_items]
    # Using a leading underscore for this internal, mutable class-level variable
    _next_simulated_id = max(known_item_ids) + 1 if known_item_ids else 1


    def on_start(self):
        """
        Called when a new user is created.
        Prints the current total number of users.
        """
        # Line too long: Breaking the f-string for better readability
        if self.environment.runner:
            print(f"Starting new user. Current total users: "
                  f"{self.environment.runner.user_count}")
        else:
            print("Starting new user (runner not available yet).")

    @task(3) # This task has a weight of 3, meaning it's 3 times more likely to run
    def get_all_items(self):
        """
        Simulates fetching all items from the API.
        """
        self.client.get("/api/items", name="/api/items [GET All]")

    @task(5) # Highest weight, most common action
    def get_single_item(self):
        """
        Simulates fetching a single item by ID.
        Attempts to get a randomly chosen existing item ID.
        """
        if self.known_item_ids:
            item_id = random.choice(self.known_item_ids)
            self.client.get(f"/api/items/{item_id}", name="/api/items/{id} [GET One]")
        else:
            # If no items are known (e.g., after deletions), try a default or skip
            self.client.get("/api/items/1", name="/api/items/{id} [GET One]") # Fallback

    @task(2) # Medium weight
    def add_new_item(self):
        """
        Simulates adding a new item to the API.
        Generates a unique item name and a random price.
        """
        item_name = f"TestItem_{self._next_simulated_id}"
        item_price = round(random.uniform(50, 500), 2)
        payload = {
            "name": item_name,
            "price": item_price
        }
        with self.client.post("/api/items", json=payload, name="/api/items [POST]") as response:
            if response.status_code == 201: # Check for successful creation
                try:
                    new_item = response.json().get('item')
                    if new_item and 'id' in new_item:
                        self.known_item_ids.append(new_item['id'])
                        self._next_simulated_id += 1 # Update _next_simulated_id
                # Catching specific JSON decoding errors
                except json.JSONDecodeError as e: # W0718: Catching specific exception
                    print(f"Error parsing response for add_new_item: {e}")
                    # Line too long: Breaking the f-string for better readability
                    response.failure(f"Could not parse response for new item ID: "
                                     f"{response.text}")
            elif response.status_code != 400: # Allow 400s (bad request, expected errors)
                # Bad indentation (W0311) fixed, and line too long (C0301) fixed
                response.failure(f"Failed to add item with status {response.status_code}: "
                                 f"{response.text}")


    @task(1) # Lowest weight, less frequent action
    def update_item(self):
        """
        Simulates updating an existing item's price.
        Chooses a random known item ID to update.
        """
        if self.known_item_ids:
            item_id = random.choice(self.known_item_ids)
            updated_price = round(random.uniform(100, 1000), 2)
            payload = {"price": updated_price}
            self.client.put(f"/api/items/{item_id}", json=payload, name="/api/items/{id} [PUT]")
        else:
            print("No items to update, skipping update task.")

    @task(0) # Weight 0 means this task won't be picked randomly, but can be called explicitly
    def delete_item(self):
        """
        Simulates deleting an item from the API.
        This task is commented out as it modifies state heavily,
        but included to show how you'd implement it.
        Uncomment and give it a weight if you want to test deletion.
        """
        # if self.known_item_ids:
        #     item_id_to_delete = random.choice(self.known_item_ids)
        #     # Line too long: Breaking the arguments for readability
        #     with self.client.delete(f"/api/items/{item_id_to_delete}",
        #                             name="/api/items/{id} [DELETE]") as response:
        #         if response.status_code == 200:
        #             self.known_item_ids.remove(item_id_to_delete)
        #         elif response.status_code != 404: # Allow 404s (item already deleted)
        #             # Line too long: Breaking the f-string for readability
        #             response.failure(f"Failed to delete item with status "
        #                              f"{response.status_code}: {response.text}")
        # else:
        #     print("No items to delete, skipping delete task.")

    def on_stop(self):
        """
        Called when a user stops.
        Prints a message indicating the user has stopped.
        """
        # W1309: Using an f-string that does not have any interpolated variables
        print("User stopped.")