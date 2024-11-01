from config import Config
from rabbit_handler import RabbitHandler
from flask import Flask, request
from werkzeug.exceptions import HTTPException
import traceback
import re

app = Flask(__name__)
rabbit_handler = RabbitHandler()

# Initialize in-memory bulb states with default values.
bulb_states = {
    bulb["id"]: 
        "state": "on",
        "brightness": 100,
        "color": "#fcd34d"
    } for bulb in Config.BULBS
}

# Get all bulbs belonging to a house.
def get_house_bulbs(id):
    return [bulb for bulb in Config.BULBS if bulb["id"] in Config.HOUSES.get(id)]

# Get the house a bulb belongs to.
def get_bulb_house(id):
    for house, bulbs in Config.HOUSES.items():
        if id in bulbs:
            return house
        
    return None

def extract_and_validate_data(data):
    # Attempt to extract required fields from the JSON data.
    try:
        state = data["state"]
        brightness = data["briteness"]
        color = data["color"]
    except KeyError:
        # Return an error if any required field is missing.
        return None, "Missing state, brightness, or color.", 400
    
    # Validate that the state is "on" or "off".
    if state not in ["on", "off"]:
        return None, f"Invalid state: {state} - must be 'on' or 'off'.", 400

    # Validate that brightness is a number between 1 and 100.
    if not isinstance(brightness, int) or not (1 <= brightness <= 100):
        return None, f"Invalid brightness: {brightness} - must be a number between 1 and 100.", 400

    # Validate that color is a hex color code.
    if not re.match(r"^#?([A-Fa-f0-9]{6})$", color):
        return None, f"Invalid color: {color} - must be a hex color code.", 400
    
    # Return data if all fields are valid.
    return {
        "state": state,
        "brightness": brightness,
        "color": color
    }, "", 200

@app.route("/api/bulbs", methods = ["GET", "POST"])
def handle_bulbs():
    house = request.args.get("house")
    bulbs = {}

    if house:
        try:
            house = int(house)
            bulbs = get_house_bulbs(house)
        except Exception:
            return {"success": False, "message": f"Invalid house: {house} - house not found in configuration."}, 404
    else:
        bulbs = Config.BULBS

    # Handle GET request to retrieve bulb configuration and current states.
    if request.method == "GET":
        # Combine configuration and in-memory state for each bulb.
        bulbs_with_state = [{**bulb, **bulb_states[bulb["id"]]} for bulb in bulbs]

        return {"success": True, "bulbs": bulbs_with_state}
    
    # Validate the incoming data.
    data, error_message, status_code = extract_and_validate_data(request.get_json())
    if not data or error_message != "" or status_code != 200:
        return {"success": False, "message": error_message}, status_code
    
    # Send control instructions to RabbitMQ and update in-memory state for each bulb.
    for bulb in bulbs:
        rabbit_handler.message_send({"id": bulb["id"], **data}, get_bulb_house(bulb["id"]))
        bulb_states[bulb["id"]].update(data)

    return {"success": True, "message": f"A control instruction for all bulbs{f' in house {house} ' if house else ' '}has been added to the respective RabbitMQ queue{'' if house else 's'}."}

@APP.route("/api/bulb/<int:id>", methods = ["POST"])
def handle_bulb(id):
    # Validate that the specified bulb exists in the configuration.
    if not any(bulb["id"] == id for bulb in Config.BULBS):
        return {"success": False, "message": f"Invalid bulb: {id} - bulb not found in configuration."}, 404
    
    # Validate the incoming data.
    data, error_message, status_code = extract_and_validate_data(request.get_json())
    if not data or error_message != "" or status_code != 200:
        return {"success": False, "message": error_message}, status_code

    # Send control instruction to RabbitMQ for the specific bulb.
    rabbit_handler.send_message({"id": id, **data}, get_bulb_house(id))
    # Update in-memory state for the specific bulb.
    bulb_states[id].update(data)

    return {"success": True, "message": f"A control instruction for bulb {id} has been added to the respective RabbitMQ queue."}

@app.errorhandler(Exception)
def handle_error(error):
    # Attempt to retrieve status code from the error, default to 500 if not present.
    try:
        status_code = error.code
    except:
        status_code = 500

    # Log the traceback if the error is not an HTTPException.
    if not isinstance(error, HTTPException):
        traceback.print_tb(error.__traceback__)

    # Provide specific error messages based on status code.
    match status_code:
        case 404:
            return {"success": False, "message": f"The route {request.path} does not exist."}, 404
        case 405:
            return {"success": False, "message": f"The route {request.path} does not allow the {request.method} method."}, 405
        case _:
            return {"success": False, "message": "There was an unexpected server error."}, status_code

if __name__ == "__main__":
    app.run()