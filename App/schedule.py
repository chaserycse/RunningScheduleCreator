import json
from http.server import SimpleHTTPRequestHandler, HTTPServer

def generate_training_plan(initial_mileage, target_mileage, duration=12):
    # Function to round to the nearest even number
    def round_to_even(num):
        return round(num / 2) * 2

    # Total increase required over the duration
    total_increase = target_mileage - initial_mileage
    increase_per_week = total_increase / (duration - 1)  # Distribute the increase across weeks

    plan = []
    current_mileage = initial_mileage

    for week in range(1, duration + 1):
        # Ensure weekly mileage is within target bounds
        weekly_mileage = round_to_even(current_mileage)  # Ensure mileage is an even number

        # Plan for a single week
        week_plan = {
            'week': week,
            'mileage': weekly_mileage,
            'schedule': []
        }

        # For 38 miles or lower, only run 5 days
        if weekly_mileage <= 38:
            week_plan['schedule'] = [
                f"Day 1: Rest",  # Monday
                f"Day 2: {round_to_even(weekly_mileage * 0.2)} miles - Aerobic",
                f"Day 3: {round_to_even(weekly_mileage * 0.15)} miles - Endurance",
                f"Day 4: {round_to_even(weekly_mileage * 0.2)} miles - Aerobic",
                f"Day 5: {round_to_even(weekly_mileage * 0.15)} miles - Recovery",
                f"Day 6: {round_to_even(weekly_mileage * 0.2)} miles - Aerobic",
                f"Day 7: {round_to_even(weekly_mileage * 0.3)} miles - Long Run"
            ]
        else:
            # For 40 miles or higher, run 6 days with 1 rest day
            week_plan['schedule'] = [
                f"Day 1: Rest",  # Monday
                f"Day 2: {round_to_even(weekly_mileage * 0.2)} miles - Aerobic",
                f"Day 3: {round_to_even(weekly_mileage * 0.15)} miles - Endurance",
                f"Day 4: {round_to_even(weekly_mileage * 0.15)} miles - Aerobic",
                f"Day 5: {round_to_even(weekly_mileage * 0.1)} miles - Recovery",
                f"Day 6: {round_to_even(weekly_mileage * 0.2)} miles - Aerobic",
                f"Day 7: {round_to_even(weekly_mileage * 0.3)} miles - Long Run"
            ]

        # Add this week's plan to the overall plan
        plan.append(week_plan)

        # Increment weekly mileage based on the calculated increase per week
        current_mileage += increase_per_week
        current_mileage = min(current_mileage, target_mileage)  # Ensure we do not exceed target mileage

    return {"plan": plan}

class RequestHandler(SimpleHTTPRequestHandler):
    def do_POST(self):
        if self.path == "/generate_training_plan":
            content_length = int(self.headers['Content-Length'])
            post_data = self.rfile.read(content_length)
            data = json.loads(post_data.decode())  # Parse the JSON data

            initial_mileage = int(data.get('initial_mileage', 0))
            target_mileage = int(data.get('target_mileage', 0))
            duration = int(data.get('duration', 12))

            # Generate the training plan
            response = generate_training_plan(initial_mileage, target_mileage, duration)

            # Send the response back as JSON
            self.send_response(200)
            self.send_header("Content-type", "application/json")
            self.end_headers()
            self.wfile.write(json.dumps(response).encode())

# Start the server
def run():
    server_address = ('', 8001)  # Use port 8001
    httpd = HTTPServer(server_address, RequestHandler)
    print("Server running on http://localhost:8001")
    httpd.serve_forever()

if __name__ == "__main__":
    run()