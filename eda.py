import matplotlib.pyplot as plt
import numpy as np
from scipy import stats
from datetime import datetime
import pandas as pd

# Load data from the Excel file
file_path = 'Untitled form (Responses).xlsx'
sheet_name = 'Form Responses 1'
df = pd.read_excel(file_path, sheet_name=sheet_name)

# Extract the "Store open time" column
opening_times = df['Store open time'].dropna().tolist()

num_stores = len(opening_times)
stores = [f"Store {i}" for i in range(1, num_stores + 1)]  # Generate labels for stores

# Convert times to numeric for plotting (minutes since midnight)
def time_to_minutes(time_str):
    time_obj = datetime.strptime(time_str, "%H:%M:%S")
    return time_obj.hour * 60 + time_obj.minute

time_in_minutes = [time_to_minutes(t) for t in opening_times]

# Calculate statistics (on numeric times)
mean_time = np.mean(time_in_minutes)
median_time = np.median(time_in_minutes)
mode_time_minutes = stats.mode(time_in_minutes, keepdims=True).mode[0]
mode_time = f"{mode_time_minutes // 60}:{mode_time_minutes % 60:02d}"

print(f"Mean: {mean_time:.2f} minutes")
print(f"Median: {median_time:.2f} minutes")
print(f"Mode: {mode_time}")

# Create a scatter plot
plt.figure(figsize=(12, 8))
plt.scatter(stores, time_in_minutes, color='teal', label='Opening Times')

# Add a trendline (linear regression)
z = np.polyfit(range(num_stores), time_in_minutes, 1)  # Fit line to data
p = np.poly1d(z)  # Create polynomial object
plt.plot(stores, p(range(num_stores)), "r--", label="Trendline")  # Plot trendline

# Rotate x-axis labels
plt.xticks(rotation=90)

# Convert y-axis labels back to time format
def minutes_to_time(minutes):
    hours = minutes // 60
    mins = minutes % 60
    return f"{hours}:{mins:02d}"

time_labels = [minutes_to_time(t) for t in range(min(time_in_minutes), max(time_in_minutes) + 1, 30)]
plt.yticks(range(min(time_in_minutes), max(time_in_minutes) + 1, 30), time_labels)

# Add labels and title
plt.title("Store Opening Times", fontsize=14)
plt.xlabel("Stores", fontsize=12)
plt.ylabel("Opening Times", fontsize=12)

# Add legend
plt.legend()

# Add gridlines
plt.grid(True, linestyle='--', alpha=0.5)

# Add figure caption
plt.figtext(0.5, -0.02, 'Figure 1 Scatter Plot for Store Opening Times', 
            wrap=True, horizontalalignment='center', fontsize=10, fontstyle='italic')

# Show the plot
plt.tight_layout()
plt.show()
