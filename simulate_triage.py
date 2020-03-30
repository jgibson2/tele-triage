import numpy as np
import matplotlib
import matplotlib.pyplot as plt

dc = 1.4 # "doubling" constant
lag_time = 4 # number of epochs before capacity is released
num_hospitals = 5
hospital_mean_capacity = 50
hospital_size_std_dev = 10
num_patients = 50000

hospital_coords = np.random.uniform(0, 1, (num_hospitals, 2))
hospital_capacities = np.round(np.random.normal(hospital_mean_capacity, hospital_size_std_dev, num_hospitals)).astype('int32')

def simulate_choose_closest_hospital(hospital_coords, hospital_capacities, num_patients, dc):
    capacities = np.copy(hospital_capacities)
    epochs = 0
    patients = np.random.uniform(0, 1, (num_patients, 2))
    not_infected = np.ones((num_patients, 1))
    track_num_infected = []
    track_capacities = []
    track_total_served = [0]
    while np.all(capacities > 0) and np.any(not_infected):
        predicted_num_infected = int(round(dc ** epochs))
        num_infected = [0 for i in range(len(hospital_capacities))]
        infected_idxs = np.random.choice(range(num_patients), min(predicted_num_infected, num_patients), replace=False)
        for idx in infected_idxs:
            if not_infected[idx]:
                if (np.any(capacities <= 0)):
                    return epochs, track_capacities, track_total_served[1:]
                hospital_choice = np.argmin(np.linalg.norm(hospital_coords - patients[idx].reshape(1, -1), axis=1))
                capacities[hospital_choice] -= 1
                num_infected[hospital_choice] += 1
                not_infected[idx] = 0
        track_num_infected.append(num_infected)
        track_total_served.append(track_total_served[-1] + np.sum(num_infected))
        track_capacities.append(capacities.copy())
        if(len(track_num_infected) - lag_time >= 0):
            replace = track_num_infected[len(track_num_infected) - lag_time]
            capacities += np.array(replace)

        epochs += 1
    return epochs, track_capacities, track_total_served[1:]

def simulate_choose_current_capacity(hospital_coords, hospital_capacities, num_patients, dc):
    capacities = np.copy(hospital_capacities)
    epochs = 0
    patients = np.random.uniform(0, 1, (num_patients, 2))
    not_infected = np.ones((num_patients, 1))
    track_num_infected = []
    track_capacities = []
    track_total_served = [0]
    while np.all(capacities > 0) and np.any(not_infected):
        predicted_num_infected = int(round(dc ** epochs))
        num_infected = [0 for i in range(len(hospital_capacities))]
        infected_idxs = np.random.choice(range(num_patients), min(predicted_num_infected, num_patients), replace=False)
        for idx in infected_idxs:
            if not_infected[idx]:
                if(np.any(capacities <= 0)):
                    return epochs, track_capacities, track_total_served[1:]
                hospital_choice = np.random.choice(range(len(hospital_capacities)), 1, p= capacities / np.sum(capacities))[0]
                capacities[hospital_choice] -= 1
                num_infected[hospital_choice] += 1
                not_infected[idx] = 0
        track_num_infected.append(num_infected)
        track_total_served.append(track_total_served[-1] + np.sum(num_infected))
        track_capacities.append(capacities.copy())
        if(len(track_num_infected) - lag_time >= 0):
            replace = track_num_infected[len(track_num_infected) - lag_time]
            capacities += np.array(replace)
        epochs += 1
    return epochs, track_capacities, track_total_served[1:]

def simulate_choose_overall_capacity(hospital_coords, hospital_capacities, num_patients, dc):
    capacities = np.copy(hospital_capacities)
    epochs = 0
    patients = np.random.uniform(0, 1, (num_patients, 2))
    not_infected = np.ones((num_patients, 1))
    track_num_infected = []
    track_capacities = []
    track_total_served = [0]
    while np.all(capacities > 0) and np.any(not_infected):
        predicted_num_infected = int(round(dc ** epochs))
        num_infected = [0 for i in range(len(hospital_capacities))]
        infected_idxs = np.random.choice(range(num_patients), min(predicted_num_infected, num_patients), replace=False)
        for idx in infected_idxs:
            if not_infected[idx]:
                if (np.any(capacities <= 0)):
                    return epochs, track_capacities, track_total_served[1:]
                hospital_choice = np.random.choice(range(len(hospital_capacities)), 1, p= np.nan_to_num(hospital_capacities / np.sum(hospital_capacities)))[0]
                capacities[hospital_choice] -= 1
                num_infected[hospital_choice] += 1
                not_infected[idx] = 0
        track_num_infected.append(num_infected)
        track_total_served.append(track_total_served[-1] + np.sum(num_infected))
        track_capacities.append(capacities.copy())
        if(len(track_num_infected) - lag_time >= 0):
            replace = track_num_infected[len(track_num_infected) - lag_time]
            capacities += np.array(replace)

        epochs += 1
    return epochs, track_capacities, track_total_served[1:]

e1, c1, t1 = simulate_choose_closest_hospital(hospital_coords, hospital_capacities, num_patients, dc)
e2, c2, t2 = simulate_choose_overall_capacity(hospital_coords, hospital_capacities, num_patients, dc)
e3, c3, t3 = simulate_choose_current_capacity(hospital_coords, hospital_capacities, num_patients, dc)

max_cap = np.max([e1, e2, e3])
max_served = np.max([t1[-1], t2[-1], t3[-1]])

plt.clf()
plt.subplot(211)
data = np.array(c1)
for i in range(data.shape[1]):
    plt.plot(range(e1), data[:, i], label=str(i))
plt.xlabel('Day')
plt.xlim(0, max_cap)
plt.ylabel('Capacity')
plt.title('Choose closest hospital')
plt.legend()

plt.subplot(212)
plt.plot(range(e1), t1, label='Total served')
plt.xlabel('Day')
plt.xlim(0, max_cap)
plt.ylim(0, max_served)
plt.ylabel('Total Served')
plt.title('Choose closest hospital')
plt.legend()
plt.show()

plt.clf()
plt.subplot(211)
data = np.array(c2)
for i in range(data.shape[1]):
    plt.plot(range(e2), data[:, i], label=str(i))
plt.xlabel('Day')
plt.xlim(0, max_cap)
plt.ylabel('Capacity')
plt.title('Choose hospital based on total capacity')
plt.legend()

plt.subplot(212)
plt.plot(range(e2), t2, label='Total served')
plt.xlabel('Day')
plt.xlim(0, max_cap)
plt.ylim(0, max_served)
plt.ylabel('Total Served')
plt.title('Choose hospital based on total capacity')
plt.legend()
plt.show()

plt.clf()
plt.subplot(211)
data = np.array(c3)
for i in range(data.shape[1]):
    plt.plot(range(e3), data[:, i], label=str(i))
plt.xlabel('Day')
plt.xlim(0, max_cap)
plt.ylabel('Capacity')
plt.title('Choose hospital based on current capacity')
plt.legend()

plt.subplot(212)
plt.plot(range(e3), t3, label='Total served')
plt.xlabel('Day')
plt.ylim(0, max_served)
plt.xlim(0, max_cap)
plt.ylabel('Total Served')
plt.title('Choose hospital based on current capacity')
plt.legend()
plt.show()