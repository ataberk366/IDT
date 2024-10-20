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
ignition_delay_time = None
ignition_temp = None

for v2 in V2:
    gas.SV = s0, v2  
    reactor = ct.IdealGasReactor(gas, energy='on')
    sim = ct.ReactorNet([reactor])
    times = np.linspace(0, 0.01, 1000)  
    temperatures = []
    pressures = []

    for t in times:
        sim.advance(t)
        temperatures.append(reactor.T)  
        pressures.append(reactor.thermo.P)

    
    temperatures = np.array(temperatures)
    temp_diff = np.diff(temperatures)
    
    
    if np.any(temp_diff > 300):
        ignition_index = np.where(temp_diff > 5)[0][0]  
        ignition_delay_time = times[ignition_index + 1]  
        ignition_temp = temperatures[ignition_index + 1]  

    all_temperatures.append(temperatures)
    all_pressures.append(pressures)

# Ignition delay time in milliseconds
ignition_delay_time_ms = ignition_delay_time * 1000 if ignition_delay_time else None

# Plotting
plt.figure(figsize=(12, 6), dpi=100)

# Temperature plot
plt.subplot(1, 2, 1) 
for temperatures in all_temperatures:
    plt.plot(times, temperatures, color='r')
plt.xlabel('Time (s)', fontsize=12)
plt.ylabel('Temperature (K)', fontsize=12)
plt.title('Temperature Change with Time', fontsize=14)
plt.grid(True)

# Ignition delay time
if ignition_delay_time:
    plt.text(0.5, -0.2, f'Ignition Delay Time: {ignition_delay_time_ms:.5f} ms\nIgnition Temperature: {ignition_temp:.2f} K', 
             horizontalalignment='center', verticalalignment='center', fontsize=12, transform=plt.gca().transAxes)

    plt.plot(ignition_delay_time, ignition_temp, marker='o', markerfacecolor='none', markeredgecolor='black', markersize=10)  
    plt.text(ignition_delay_time + 0.0005, ignition_temp, 'Ignition Point', fontsize=10, verticalalignment='center')

else:
    plt.text(0.5, -0.2, "Ignition did not occur.", 
             horizontalalignment='center', verticalalignment='center', fontsize=12, transform=plt.gca().transAxes)

# Pressure plot (in atm)
plt.subplot(1, 2, 2)  
for pressures in all_pressures:
    plt.plot(times, pressures, color='b')
plt.xlabel('Time (s)', fontsize=12)
plt.ylabel('Pressure (atm)', fontsize=12)
plt.title('Pressure Change with Time', fontsize=14)
plt.grid(True)

plt.tight_layout() 
plt.show()
