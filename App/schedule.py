from urllib.parse import parse_qs
import json
from http.server import SimpleHTTPRequestHandler, HTTPServer

import re

def generate_schedule(total_mileage, workout_type):
    schedule = []  
    
    # Adjust long run percentage based on total mileage
    if total_mileage < 40:
        long_run_percentage = 0.35  # For mileage less than 40, the long run will be 35% of the total mileage
    else:
        long_run_percentage = 0.20  # For higher mileage, the long run remains 20%

    # Calculate long run mileage
    long_run_mileage = total_mileage * long_run_percentage
    
    # Training days and rest days based on the total mileage
    training_days = 6 if total_mileage > 41 else 5
    rest_days = 7 - training_days

    # Remaining mileage for easy runs and recovery
    remaining_mileage = total_mileage - long_run_mileage
    # Easy run mileage will be divided evenly across training days (minus one for the long run)
    mileage_per_run = remaining_mileage // (training_days - 1)

    # Calculate recovery run mileage (75% of the mileage_per_run for the easy run)
    recovery_run_mileage = mileage_per_run * 0.75
    
    # Total calculated mileage
    total_calculated_mileage = long_run_mileage + (mileage_per_run * (training_days - 1)) + recovery_run_mileage
    
    # If the total calculated mileage is less than total_mileage due to integer division, add the difference to the last run
    if total_calculated_mileage < total_mileage:
        mileage_per_run += total_mileage - total_calculated_mileage

    # Now build the schedule
    day_counter = 0
    recovery_run_added = False
    while day_counter < 7:
        if day_counter in [3, 6][:rest_days]:  # Rest days
            schedule.append(f"Day {day_counter + 1}: Rest Day")
        elif day_counter == 4:  # Long run day
            schedule.append(f"Day {day_counter + 1}: Long Run - {long_run_mileage:.1f} miles")
        elif not recovery_run_added and day_counter != 4:  # Add recovery run once
            schedule.append(f"Day {day_counter + 1}: Recovery Run - {recovery_run_mileage:.1f} miles")
            recovery_run_added = True
        else:  # Easy run day
            schedule.append(f"Day {day_counter + 1}: Easy Run - {mileage_per_run:.1f} miles")
        day_counter += 1

    # Double check if total mileage is accurate using regular expression to extract mileage
    calculated_total = 0
    for line in schedule:
        # Extract the numeric part after the "Run - " keyword
        match = re.search(r'(\d+(\.\d+)?) miles', line)
        if match:
            calculated_total += float(match.group(1))
    
    print(f"Calculated Total Mileage: {calculated_total}")
    return {"schedule": schedule}

class RequestHandler(SimpleHTTPRequestHandler):
    def do_POST(self):
        if self.path == "/generate_schedule":
            content_length = int(self.headers['Content-Length'])
            post_data = self.rfile.read(content_length)
            form = parse_qs(post_data.decode())

            mileage = form.get('mileage', [''])[0]
            workout_type = form.get('workout_type', [''])[0]

            total_mileage = int(mileage)
            response = generate_schedule(total_mileage, workout_type)

            self.send_response(200)
            self.send_header("Content-type", "application/json")
            self.end_headers()
            self.wfile.write(json.dumps(response).encode())

# Start the server
def run():
    server_address = ('', 8001)  # Use port 8001 instead of 8000 if 8000 is in use
    httpd = HTTPServer(server_address, RequestHandler)
    print("Server running on http://localhost:8001")
    httpd.serve_forever()

if __name__ == "__main__":
    run()









