import requests
import matplotlib.pyplot as plt

try:
    # Fetch data from FastAPI
    response = requests.get('http://127.0.0.1:8000/fetch_stock_data/')
    response.raise_for_status()  # Raise an HTTPError for bad responses
    data = response.json()

    # Extract flow_accum data
    intervals = [item['interval'] for item in data['usd_data']]
    flow_accum = [item['flow_accum'] for item in data['usd_data']]

    # Plot
    plt.figure(figsize=(12, 6))
    plt.plot(intervals, flow_accum, marker='o', linestyle='-')
    plt.xlabel('Time Interval')
    plt.ylabel('Cumulative Flow')
    plt.title('Cumulative Flow Over Time')
    plt.xticks(rotation=45, ha='right')
    plt.tight_layout()

    # Save the plot as an image
    plt.savefig('flow_accum_plot.png')

    # Show the plot
    plt.show()

except requests.exceptions.RequestException as e:
    print(f"Error fetching data: {e}")
