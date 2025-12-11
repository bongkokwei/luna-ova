from luna_ova import LunaOVA
import numpy as np
import matplotlib.pyplot as plt


def measure_device(centre_wl=1550, wl_range=40, averages=10):
    """
    Perform a complete measurement on a device under test.

    Parameters:
        centre_wl: Centre wavelength in nm
        wl_range: Wavelength range in nm
        averages: Number of averages
    """
    # Initialise and connect
    ova = LunaOVA(ip="130.194.137.122")

    try:
        # Connect
        print("Connecting to Luna OVA...")
        device_id = ova.connect()
        print(f"Connected: {device_id}")

        # Get DUT length
        dut_length = ova.get_dut_length()
        print(f"DUT Length: {dut_length:.2f} m")

        # Configure measurement
        print(f"\nConfiguring measurement:")
        print(f"  Centre wavelength: {centre_wl} nm")
        print(f"  Wavelength range: {wl_range} nm")
        print(f"  Averages: {averages}")

        actual_cwl = ova.set_center_wavelength(centre_wl)
        actual_range = ova.set_wavelength_range(wl_range)
        ova.set_averaging(averages)

        resolution = ova.get_sample_resolution()
        num_points = ova.get_number_of_points()
        print(f"  Sample resolution: {resolution:.4f} nm")
        print(f"  Number of points: {num_points}")

        # Perform scan
        print("\nScanning...")
        ova.scan(num_averages=averages)
        print("Scan complete!")

        # Retrieve data
        print("\nRetrieving data...")
        wavelength = ova.get_wavelength_axis()
        il = ova.get_insertion_loss()
        gd = ova.get_group_delay()
        lpd = ova.get_linear_phase_deviation()

        # Plot results
        fig, axes = plt.subplots(3, 1, figsize=(10, 12))

        axes[0].plot(wavelength, il, "b-", linewidth=1)
        axes[0].set_xlabel("Wavelength (nm)")
        axes[0].set_ylabel("Insertion Loss (dB)")
        axes[0].set_title("Insertion Loss")
        axes[0].grid(True, alpha=0.3)

        axes[1].plot(wavelength, gd, "r-", linewidth=1)
        axes[1].set_xlabel("Wavelength (nm)")
        axes[1].set_ylabel("Group Delay (ps)")
        axes[1].set_title("Group Delay")
        axes[1].grid(True, alpha=0.3)

        axes[2].plot(wavelength, lpd, "g-", linewidth=1)
        axes[2].set_xlabel("Wavelength (nm)")
        axes[2].set_ylabel("Linear Phase Deviation (rad)")
        axes[2].set_title("Linear Phase Deviation")
        axes[2].grid(True, alpha=0.3)

        plt.tight_layout()
        plt.savefig("ova_measurement.png", dpi=300)
        plt.show()
        print("\nPlot saved as 'ova_measurement.png'")

        return wavelength, il, gd, lpd

    finally:
        # Always disconnect
        ova.disconnect()
        print("\nDisconnected from Luna OVA")


if __name__ == "__main__":

    wavelength, il, gd, lpd = measure_device(
        centre_wl=1550,
        wl_range=2,
        averages=5,
    )
