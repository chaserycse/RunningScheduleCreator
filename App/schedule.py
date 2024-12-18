import json
from http.server import SimpleHTTPRequestHandler, HTTPServer
from urllib.parse import parse_qs, urlparse

# Function to generate running schedule
def generate_schedule(total_mileage, workout_type):
    schedule = []
    if workout_type == "Easy Runs":
        weekly_runs = 5  # Assume 5 easy runs per week
        mileage_per_run = total_mileage // weekly_runs
        for i in range(weekly_runs):
            schedule.append(f"Day {i+1}: Easy Run - {mileage_per_run} miles")
    elif workout_type == "Interval Training":
        weekly_runs = 3  # 3 runs with intervals
        mileage_per_run = total_mileage // weekly_runs
        for i in range(weekly_runs):
            schedule.append(f"Day {i+1}: Interval Run - {mileage_per_run} miles")
    else:
        # Mixed schedule with easy runs, long runs, etc.
        schedule.append(f"Day 1: Easy Run - {total_mileage // 7} miles")
        schedule.append(f"Day 2: Easy Run - {total_mileage // 7} miles")
        schedule.append(f"Day 3: Interval Training - {total_mileage // 10} miles")
        schedule.append(f"Day 4: Easy Run - {total_mileage // 7} miles")
        schedule.append(f"Day 5: Long Run - {total_mileage // 4} miles")
        schedule.append(f"Day 6: Easy Run - {total_mileage // 7} miles")
        schedule.append(f"Day 7: Rest Day")
    
    return schedule

# Request handler to process the form input and generate the schedule
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
            # Parse form data from the request
            content_length = int(self.headers['Content-Length'])
            post_data = self.rfile.read(content_length)
            data = parse_qs(post_data.decode('utf-8'))

            total_mileage = int(data['mileage'][0])
            workout_type = data['workout_type'][0]

            # Generate the running schedule
            schedule = generate_schedule(total_mileage, workout_type)

            # Send the response as a JSON object
            self.send_response(200)
            self.send_header("Content-type", "application/json")
            self.end_headers()
            self.wfile.write(json.dumps(schedule).encode())

# Start the HTTP server
def run():
    server_address = ('', 8000)  # Localhost, port 8000
    httpd = HTTPServer(server_address, RequestHandler)
    print("Server running on http://localhost:8000")
    httpd.serve_forever()

if __name__ == '__main__':
    run()
