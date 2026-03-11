import pandas as pd
import matplotlib.pyplot as plt
import numpy as np

# Load CSV file
data = pd.read_csv("dataset.csv")   # change filename if needed

# List of plots to generate (x, y)
plots = [
    ("w1", "gain_max_dB"),
    ("w3", "gain_max_dB"),
    ("w5", "gain_max_dB"),
    ("w1", "pm"),
    ("w3", "pm"),
    ("w5", "pm"),
    ("w1", "gbw"),
    ("w3", "gbw"),
    ("w5", "gbw"),
]

names = {
    "w1": "W1/W2 (PMOS Pair)",
    "w3": "W3/W4 (NMOS Pair)",
    "w5": "W5/W6 (Current Mirror)",
    "gain_max_dB": "DC Gain (Av)",
    "pm": "Phase Margin (deg)",
    "gbw": "Gain-Bandwidth Product (Hz)"
}

# Generate and save plots
for x, y in plots:
    x_vals = data[x]
    y_vals = data[y]

    plt.figure()

    # Scatter plot
    plt.scatter(x_vals, y_vals, s=5, alpha=0.4)

    # Line of best fit
    slope, intercept = np.polyfit(x_vals, y_vals, 1)
    x_line = np.linspace(x_vals.min(), x_vals.max(), 100)
    y_line = slope * x_line + intercept
    plt.plot(x_line, y_line, color='red')

    # Calculate regression coefficient (R-squared)
    y_pred = slope * x_vals + intercept
    ss_total = np.sum((y_vals - np.mean(y_vals))**2)
    ss_residual = np.sum((y_vals - y_pred)**2)
    r_squared = 1 - (ss_residual / ss_total)

    # Add R-squared to the plot
    plt.text(0.05, 0.95, f"R² = {r_squared:.2f}", transform=plt.gca().transAxes, fontsize=10, verticalalignment='top')

    # Labels
    plt.xlabel(x)
    plt.ylabel(y)
    plt.title(f"{names[x]} vs {names[y]}")
    plt.grid(True)

    # Save file
    filename = f"images/{x}_vs_{y}.png"
    plt.savefig(filename, dpi=300)
    plt.close()

print("All plots saved.")