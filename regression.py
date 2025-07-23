def simulate(car, max_seconds=3):

    print("go forward")
    car.forward()
    time.sleep(max_seconds)
    print("done driving at speed", car.speed)

def run_tests(speeds, car, max_seconds=3):
    results = []
    print(f"Simulating each speed for {max_seconds} seconds...\n")
    for speed in speeds:
        print(f"Testing speed: {speed}")
        car.set_speed(speed)
        input("Press Enter to start driving...\n")
        simulate(car, max_seconds)
        car.instant_stop()
        results.append((speed, max_seconds))
        input("Press Enter to continue to the next speed...\n")
    return results

def prompt_user_for_distances(speeds):
    print("\nNow enter the real-world distances moved at each test speed.\n")
    distances = []
    for s in speeds:
        d = float(input(f"Distance travelled at speed {s}: "))
        distances.append(d)
    return distances

def estimate_base_speed(speeds, times, distances):
    rates = np.array(distances) / np.array(times)  # real units per second
    speeds = np.array(speeds)
    speeds_with_const = sm.add_constant(speeds)  # adds intercept term

    model = sm.OLS(rates, speeds_with_const).fit()

    base_units_per_second = model.params[1] * 1 + model.params[0]  # slope * 1 + intercept

    print(f"\nEstimated: speed = 1 corresponds to ~{base_units_per_second:.4f} real units/second.")
    print(model.summary())  # Optional: shows regression details

    return model


def main():
    
    car = JMotor()
    try:
        test_speeds = [1, 2, 3, 5]
        results = run_tests(test_speeds, car)

        input("\nPress Enter when ready to enter measured distances...\n")
        speeds = [r[0] for r in results]
        times = [r[1] for r in results]
        distances = prompt_user_for_distances(speeds)

        estimate_base_speed(speeds, times, distances)
    finally:
        print("done")
if __name__ == "__main__":
    main()