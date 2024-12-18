import json
from http.server import SimpleHTTPRequestHandler, HTTPServer
import cgi  # For parsing multipart/form-data

# Function to generate running schedule
def generate_schedule(total_mileage, workout_type):
    schedule = []

    # Determine the number of training days based on total mileage
    if total_mileage <= 41:
        training_days = 5
    elif 42 <= total_mileage <= 65:
        training_days = 6
    else:
        training_days = 7

    # Calculate long run mileage (20% of total mileage)
    long_run_mileage = total_mileage * 0.20  # 20% of total mileage

    # Determine the day placement of rest days (for 5 training days, there should be 2 rest days)
    rest_days = 7 - training_days
    rest_day_indices = []

    # For a 5-day training schedule, place rest days in such a way that there are 3 training days in between
    if training_days == 5:
        rest_day_indices = [3]  # Rest on the 4th day (Day 4)
    elif training_days == 6:
        rest_day_indices = [6]  # Rest on the 7th day (Day 7)

    # Set up day counter
    day_counter = 0

    # Remaining mileage excluding the long run
    remaining_mileage = total_mileage - long_run_mileage

    # Calculate the mileage for each training day (excluding long run day)
    mileage_per_run = remaining_mileage // (training_days - 1)

    while day_counter < 7:
        if day_counter in rest_day_indices:
            schedule.append(f"Day {day_counter + 1}: Rest Day")
        else:
            # Since we're focusing only on "Easy Runs", we can directly assign it here
            run_type = "Easy Run"

            # Assign long run on the appropriate day (usually Day 5 for 6 or 7 days of training)
            if day_counter == 4 and training_days > 5:  # Place long run on Day 5 for 6 or 7 days of training
                schedule.append(f"Day {day_counter + 1}: Long Run - {long_run_mileage:.1f} miles")
            else:
                schedule.append(f"Day {day_counter + 1}: {run_type} - {mileage_per_run} miles")
        
        day_counter += 1

    return schedule

# Request handler for HTTP requests
class RequestHandler(SimpleHTTPRequestHandler):
    def do_GET(self):
        if self.path == "/":
            # Serve the HTML form
            self.send_response(200)
            self.send_header("Content-type", "text/html")
            self.end_headers()
            self.wfile.write(open('index.html', 'rb').read())
        else:
            super().do_GET()

    def do_POST(self):
        if self.path == "/generate_schedule":
            # Parse the form data
            content_type, _ = self.headers.get('Content-Type').split(';', 1)
            if content_type == 'multipart/form-data':
                # Use cgi.FieldStorage to parse multipart form data
                form = cgi.FieldStorage(fp=self.rfile, headers=self.headers, environ={'REQUEST_METHOD': 'POST'})
                mileage = form.getvalue('mileage')
                workout_type = form.getvalue('workout_type')
            else:
                # Handle case if content-type is something else
                self.send_response(400)
                self.send_header("Content-type", "application/json")
                self.end_headers()
                self.wfile.write(json.dumps({"error": "Unsupported content type"}).encode())
                return
            
            try:
                # Ensure mileage is an integer
                total_mileage = int(mileage)
                # Generate the running schedule
                schedule = generate_schedule(total_mileage, workout_type)
                
                # Send the response as a JSON object
                self.send_response(200)
                self.send_header("Content-type", "application/json")
                self.end_headers()
                self.wfile.write(json.dumps(schedule).encode())
            
            except (ValueError, TypeError):
                # Handle errors in case of invalid data
                self.send_response(400)
                self.send_header("Content-type", "application/json")
                self.end_headers()
                self.wfile.write(json.dumps({"error": "Invalid mileage value"}).encode())

# Start the HTTP server
def run():
    server_address = ('', 8000)  # Localhost, port 8000
    httpd = HTTPServer(server_address, RequestHandler)
    print("Server running on http://localhost:8000")
    httpd.serve_forever()

if __name__ == '__main__':
    run()




