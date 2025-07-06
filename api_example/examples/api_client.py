import requests
import json
from datetime import datetime
from typing import Dict, Any, Optional

class MinuteEmpireClient:
    def __init__(self, base_url: str = "http://localhost:8000"):
        self.base_url = base_url
        self.session = requests.Session()
        self.token = None

    def login(self, username: str, password: str) -> Dict[str, Any]:
        """Login to get authentication token"""
        response = self.session.post(
            f"{self.base_url}/login",
            json={"username": username, "password": password}
        )
        response.raise_for_status()
        data = response.json()
        self.token = data["access_token"]
        return data

    def get_current_user(self) -> Dict[str, Any]:
        """Get information about the currently logged in user"""
        response = self.session.get(
            f"{self.base_url}/me",
            cookies={"minute_empire_token": self.token}
        )
        response.raise_for_status()
        return response.json()

    def get_my_villages(self) -> Dict[str, Any]:
        """Get all villages owned by the current user"""
        response = self.session.get(
            f"{self.base_url}/villages/me",
            cookies={"minute_empire_token": self.token}
        )
        response.raise_for_status()
        return response.json()

    def execute_command(self, village_id: str, command: str) -> Dict[str, Any]:
        """Execute a command on a village
        
        Args:
            village_id (str): The ID of the village to execute the command on
            command (str): The command string to execute. Examples:
                - "create wood field in 1"
                - "upgrade building in 1"
                - "train 10 militia"
                - "create barraks building in 2"
                - "move troop_123 to 10,20"
                - "set stance for troop_123 to defensive"
        
        Returns:
            Dict[str, Any]: The response from the server
        """
        response = self.session.post(
            f"{self.base_url}/villages/command",
            json={"village_id": village_id, "command": command},
            cookies={"minute_empire_token": self.token}
        )
        response.raise_for_status()
        return response.json()

    def get_map_info(self) -> Dict[str, Any]:
        """Get map information including bounds and all villages"""
        response = self.session.get(
            f"{self.base_url}/map/info",
            cookies={"minute_empire_token": self.token}
        )
        response.raise_for_status()
        return response.json()

    def rename_village(self, village_id: str, new_name: str) -> Dict[str, Any]:
        """Rename a village"""
        response = self.session.put(
            f"{self.base_url}/villages/{village_id}/rename",
            json={"name": new_name},
            cookies={"minute_empire_token": self.token}
        )
        response.raise_for_status()
        return response.json()

def main():
    # Initialize client
    client = MinuteEmpireClient("http://localhost:8000")  # Change URL as needed

    try:
        # Login
        print("Logging in...")
        login_result = client.login("testapi", "testapi123")
        print(f"Logged in successfully as {login_result['username']}")

        # Get user info
        print("\nGetting user info...")
        user_info = client.get_current_user()
        print(f"User ID: {user_info['id']}")
        print(f"Family Name: {user_info['family_name']}")

        # Get villages
        print("\nGetting villages...")
        villages = client.get_my_villages()
        for village in villages:
            print(f"\nVillage: {village['name']}")
            print(f"Location: ({village['location']['x']}, {village['location']['y']})")
            print("Resources:")
            print(f"Debug - Resources structure: {json.dumps(village['resources'], indent=2)}")
            for resource, info in village['resources'].items():
                if isinstance(info, dict):
                    print(f"  {resource}: {info.get('current', 0)}/{info.get('capacity', 0)} (Rate: {info.get('rate', 0)}/h)")
                else:
                    print(f"  {resource}: {info}")

            # Example: Execute some commands
            print("\nExecuting commands...")
            
            # Example 1: Create a wood field
            command = "create wood field in 3"  # Create a wood field in slot 1
            result = client.execute_command(village['id'], command)
            print(f"Create wood field result: {result['message']}")

            # Example 2: Upgrade city center
            command = "upgrade building in 1"  # Upgrade building in slot 1
            result = client.execute_command(village['id'], command)
            print(f"Upgrade building result: {result['message']}")

            # Example 3: Train troops
            command = "train 10 militia"  # Train 10 militia units
            result = client.execute_command(village['id'], command)
            print(f"Train troops result: {result['message']}")

            # Example 4: Create a building
            command = "create barraks building in 2"  # Create barraks in slot 2
            result = client.execute_command(village['id'], command)
            print(f"Create barraks result: {result['message']}")

            # Example 5: Send troops (assuming we have a troop with ID 'troop_123')
            command = "move troop_123 to 10,20"  # Move troops to coordinates (10,20)
            result = client.execute_command(village['id'], command)
            print(f"Move troops result: {result['message']}")

            # Example 6: Set troop stance
            command = "set stance for troop_123 to defensive"  # Set troop stance to defensive
            result = client.execute_command(village['id'], command)
            print(f"Set stance result: {result['message']}")

        # Get map information
        print("\nGetting map information...")
        map_info = client.get_map_info()
        print(f"Map bounds: {map_info['map_bounds']}")
        print(f"Total villages on map: {len(map_info['villages'])}")

    except requests.exceptions.RequestException as e:
        print(f"Error occurred: {e}")
        if hasattr(e.response, 'json'):
            print(f"Error details: {e.response.json()}")

if __name__ == "__main__":
    main() 