import pandas as pd
import numpy as np
import matplotlib.pyplot as plt


def read_csv(file_path: str) -> pd.DataFrame:
    df: pd.DataFrame = pd.read_csv(file_path)
    df["Label"] = ""                    # Create new column for Labeling
    return df

def label_data(df: pd.DataFrame) -> pd.DataFrame:
    df.loc[df["velocity"] >= 120, "Label"] = "120+"
    return df

def clean_data(df: pd.DataFrame) -> pd.DataFrame:
    df = df.replace(["null", "NaN"], np.nan)
    df = df.dropna()
    df = df.reset_index(drop=True)
    return df

def matching_trips(df: pd.DataFrame) -> list:
    trips = (
        df.loc[df["velocity"] >= 120, "tripId"]
        .drop_duplicates()
        .tolist()
    )
    print("tripIds for >= 120 km/h calculation:", trips[0], "and", trips[1])

    return trips

def draw_plot(df: pd.DataFrame) -> None:
    # Get Data
    velocity = df["velocity"]
    temperature = df["temperatureRotorBack"]
    time = (df["timeUnix"] - df["timeUnix"].iloc[0]) / 1000

    # Plot Data for Velocity and TemperatureRotorBack in one Graph
    plt.figure(figsize=(20, 10))
    plt.plot(time,
             velocity,
             marker=".",
             linestyle="-",
             color="b",
             label="Velocity"
             )
    plt.plot(time,
             temperature,
             marker=".",
             linestyle="-",
             color="r",
             label="Temperature"
             )

    # Limits for Time 0-1100, Velocity 0-200)
    plt.xlim(0, 1100)
    plt.ylim(0, 200)

    plt.title("Velocity and Temperature over Time:", fontsize=14, fontweight="bold")
    plt.xlabel("time in [s]", fontsize=12)
    plt.ylabel("velocity in [km/h] and temperature in [°C]", fontsize=12)

    plt.grid(True, linestyle="-", alpha=1.0)
    plt.legend()

    # Display Plot
    plt.tight_layout()
    plt.show()

def calc_average_temp(df: pd.DataFrame) -> None:
    greater = df[df["velocity"] >= 120]
    lower = df[df["velocity"] < 120]

    print("Average temperatureRotorBack for >= 120 km/h:", greater["temperatureRotorBack"].mean(), "°C")
    print("Average temperatureRotorBack for < 120 km/h:", lower["temperatureRotorBack"].mean(), "°C\n")



def calc_correlation(df: pd.DataFrame) -> None:
    correlation_back = df["velocity"].corr(df["temperatureRotorBack"])
    correlation_front = df["velocity"].corr(df["temperatureRotorFront"])

    print("Correlation between Velocity and TemperatureRotorBack =", correlation_back)
    print("Correlation between Velocity and TemperatureRotorFront =", correlation_front, "\n")


def create_histograms(df: pd.DataFrame) -> None:
    # Create Histogram Data
    greater = df.loc[df["velocity"] >= 120, "temperatureRotorBack"]
    lower = df.loc[df["velocity"] < 120, "temperatureRotorBack"]

    cluster_size = 5
    all_values = pd.concat([greater, lower])

    bins = np.arange(
        all_values.min() - all_values.min() % cluster_size,
        all_values.max() + cluster_size,
        cluster_size
    )

    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(15, 5), sharey=True)

    # Left Graph: Temp RotorBack for velocity >= 120 km/h
    ax1.hist(greater, bins=bins, color='skyblue', edgecolor='black', alpha=0.8)
    ax1.set_title("Histogram: temperatureRotorBack for velocity ≥ 120 km/h", fontweight='bold')
    ax1.set_xlabel("Temperatur in [°C]")
    ax1.set_ylabel("Frequency")
    ax1.set_xticks(bins)
    ax1.tick_params(axis='x', rotation=45)
    ax1.grid(axis='y', linestyle='--', alpha=0.5)

    # Right Graph: Temp RotorBack for velocity < 120 km/h
    ax2.hist(lower, bins=bins, color='lightcoral', edgecolor='black', alpha=0.8)
    ax2.set_title("Histogram: temperatureRotorBack for velocity < 120 km/h", fontweight='bold')
    ax2.set_xlabel("Temperatur in [°C]")
    ax2.set_xticks(bins)
    ax2.tick_params(axis='x', rotation=45)
    ax2.grid(axis='y', linestyle='--', alpha=0.5)

    # Show Plot
    plt.tight_layout()
    plt.show()


def calc_driving_statistics_laps(df: pd.DataFrame) -> float:
    start_val = df.iloc[0]["timeUnix"]/1000     # convert to seconds
    end_val = df.iloc[-1]["timeUnix"]/1000      # convert to seconds

    return end_val - start_val

def calc_driving_statistics_average_vel(df: pd.DataFrame) -> float:

    return df["velocity"].mean()


#data_path = 'C:/Users/stras/Desktop/TestDataRotor (1).csv'
data_path = 'data/TestDataRotor (1).csv'

# Press the green button in the gutter to run the script.
if __name__ == '__main__':

    # Read CSV to Pandas DataFrame
    trip_data = read_csv(data_path)

    # Remove corrupted Data like null or NaN
    trip_data = clean_data(trip_data)

    # Lable Data with Velocity Value of 120 and higher
    labeled_data = label_data(trip_data)

    # Find matching Vehicles and Trips
    trips_120plus = matching_trips(labeled_data)

    # Create Groups and group by tripId
    trips = labeled_data.groupby("tripId")
    trip_names = list(trips.groups.keys())
    trip1 = trips.get_group(trips_120plus[0])
    trip2 = trips.get_group(trips_120plus[1])

    # Plot v(t) and T(t)
    draw_plot(trip1)

    # Calculate average RotorBack temperatures for >= 120 and < 120
    calc_average_temp(labeled_data)

    # Calculate Correlation
    calc_correlation(labeled_data)

    # Create Histograms of TemperatureRotorBack for Velocities >= 120 km/h and < 120 km/h
    create_histograms(labeled_data)

    lap_times = []
    average_velocities = []

    for trip in trip_names:
        group = trips.get_group(trip)

        lap_times.append(
            calc_driving_statistics_laps(group)
        )

        average_velocities.append(
            calc_driving_statistics_average_vel(group)
        )

    print("Longest LapTime:", max(lap_times), "seconds")
    print("Shortest LapTime:", min(lap_times), "seconds\n")

    print("Highest Average Velocity:", max(average_velocities), "km/h")
    print("Lowest Average Velocity:", min(average_velocities), "km/h\n")