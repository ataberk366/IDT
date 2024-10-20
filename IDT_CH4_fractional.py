import cantera as ct
import numpy as np
import matplotlib.pyplot as plt

# Setup
gas = ct.Solution("gri30.yaml")
gas.TPX = 273.15, ct.one_atm, 'CH4:1.0, O2:2.0, N2:7.52'
V1 = 1  # Initial volume
V2 = np.linspace(1, 0.02, 100)  # Final volume range

# Isentropic Approach
s0 = gas.entropy_mass

# Initialize lists for plotting
all_temperatures = []
all_pressures = []
all_co2_fractions = []
ignition_delay_time = None
ignition_temp = None
ignition_fraction = None

for v2 in V2:
    gas.SV = s0, v2  
    reactor = ct.IdealGasReactor(gas, energy='on')
    sim = ct.ReactorNet([reactor])
    times = np.linspace(0, 0.01, 1000)  
    temperatures = []
    pressures = []
    co2_fractions = []

    for t in times:
        sim.advance(t)
        temperatures.append(reactor.T)  
        pressures.append(reactor.thermo.P)
        co2_fractions.append(gas.mole_fraction_dict().get('CO2', 0)) 

    temperatures = np.array(temperatures)
    temp_diff = np.diff(temperatures)

    if ignition_delay_time is None and np.any(np.array(co2_fractions) > 0.00001):
        ignition_index = np.where(np.array(co2_fractions) > 0.0002)[0][0]
        ignition_delay_time = times[ignition_index]
        ignition_temp = temperatures[ignition_index]
        ignition_fraction = co2_fractions[ignition_index]

    all_temperatures.append(temperatures)
    all_pressures.append(pressures)
    all_co2_fractions.append(co2_fractions)

# Ignition delay time in milliseconds
ignition_delay_time_ms = ignition_delay_time * 1000 if ignition_delay_time else None

# Plotting
plt.figure(figsize=(12, 8), dpi=100)

# Temperature plot
plt.subplot(2, 2, 1) 
for temperatures in all_temperatures:
    plt.plot(times, temperatures, color='r')
plt.xlabel('Time (s)', fontsize=12)
plt.ylabel('Temperature (K)', fontsize=12)
plt.title('Temperature Change with Time', fontsize=14)
plt.grid(True)

# CO2 Mole Fraction plot
plt.subplot(2, 2, 3)
for co2_fractions in all_co2_fractions:
    plt.plot(times, co2_fractions, color='g')
plt.xlabel('Time (s)', fontsize=12)
plt.ylabel('CO2 Mole Fraction', fontsize=12)
plt.title('CO2 Mole Fraction Change with Time', fontsize=14)
plt.grid(True)

# Marking the ignition point on the temperature plot
if ignition_delay_time:
    # Pressure plot (in atm)
    plt.subplot(2, 2, 2)  
    for pressures in all_pressures:
        plt.plot(times, pressures, color='b')
    plt.xlabel('Time (s)', fontsize=12)
    plt.ylabel('Pressure (atm)', fontsize=12)
    plt.title('Pressure Change with Time', fontsize=14)
    plt.grid(True)

    # Ignition point marker
    plt.subplot(2, 2, 1)
    plt.plot(ignition_delay_time, ignition_temp, 'ko', markersize=8, markerfacecolor='none')  # Mark the ignition point
    plt.text(ignition_delay_time + 0.0001, ignition_temp, 'Ignition Point', fontsize=10, verticalalignment='center')

    # Text for ignition details
    plt.subplot(2, 2, 4)
    plt.axis('off')  # Turn off the axes
    plt.text(0.1, 0.5, f'Ignition Delay Time: {ignition_delay_time_ms:.5f} ms\nIgnition Temperature: {ignition_temp:.2f} K\nCO2 Mole Fraction: {ignition_fraction:.4f}', 
             fontsize=12, verticalalignment='center', horizontalalignment='left')
else:
    plt.subplot(2, 2, 4)
    plt.axis('off')
    plt.text(0.1, 0.5, "Ignition did not occur.", fontsize=12, verticalalignment='center')

plt.tight_layout(rect=[0, 0, 1, 0.95])  # Adjust layout to make space for text
plt.show()
