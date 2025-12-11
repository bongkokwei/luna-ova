"""
Luna OVA (Optical Vector Analyzer) Python Interface

This module provides a Python interface for controlling Luna OVA optical vector analyzers
via TCP/IP connection. It replicates the functionality from the MATLAB implementation.

Author: Converted from MATLAB code
"""

import socket
import time
import numpy as np
from typing import Tuple, Optional, Dict


class LunaOVA:
    """
    Python interface for Luna Optical Vector Analyzer (OVA).

    This class provides methods to connect to, configure, and acquire measurements
    from a Luna OVA device via TCP/IP.

    Attributes:
        ip (str): IP address of the Luna OVA device
        port (int): TCP port for communication (default: 1)
        timeout (float): Socket timeout in seconds
        buffer_size (int): Size of input/output buffers
        socket (socket.socket): TCP socket connection
    """

    def __init__(
        self,
        ip: str = "130.194.137.137",
        port: int = 1,
        timeout: float = 0.1,
        buffer_size: int = 2**19,
    ):
        """
        Initialize Luna OVA connection parameters.

        Args:
            ip: IP address of the Luna OVA device
            port: TCP port for communication
            timeout: Socket timeout in seconds
            buffer_size: Size of buffers for data transfer
        """
        self.ip = ip
        self.port = port
        self.timeout = timeout
        self.buffer_size = buffer_size
        self.socket: Optional[socket.socket] = None
        self._connected = False

    def connect(self) -> str:
        """
        Establish TCP/IP connection to the Luna OVA device.

        Returns:
            Device identification string

        Raises:
            ConnectionError: If connection fails
        """
        try:
            # Close existing connection if any
            if self._connected:
                self.disconnect()

            # Create TCP socket
            self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.socket.settimeout(self.timeout)
            self.socket.setsockopt(
                socket.SOL_SOCKET, socket.SO_RCVBUF, self.buffer_size
            )
            self.socket.setsockopt(
                socket.SOL_SOCKET, socket.SO_SNDBUF, self.buffer_size
            )

            # Connect to device
            self.socket.connect((self.ip, self.port))
            self._connected = True

            # Verify connection with identification query
            idn = self.query("*IDN?")
            print(f"Connected to: {idn}")
            return idn

        except Exception as e:
            self._connected = False
            raise ConnectionError(
                f"Failed to connect to Luna OVA at {self.ip}:{self.port}. Error: {e}"
            )

    def disconnect(self):
        """Close the connection to the Luna OVA device."""
        if self.socket:
            try:
                self.socket.close()
            except:
                pass
            finally:
                self.socket = None
                self._connected = False

    def _flush_input(self):
        """
        Flush the input buffer by reading and discarding any pending data.
        """
        # if not self._connected or not self.socket:
        #     return

        # # Temporarily set non-blocking mode
        # self.socket.setblocking(False)
        # try:
        #     while True:
        #         try:
        #             self.socket.recv(self.buffer_size)
        #         except (BlockingIOError, socket.error):
        #             break
        # finally:
        #     # Restore blocking mode
        #     self.socket.setblocking(True)

    def _send(self, command: str):
        """
        Send a command to the device.

        Args:
            command: SCPI command string

        Raises:
            RuntimeError: If not connected
        """
        if not self._connected or not self.socket:
            raise RuntimeError("Not connected to Luna OVA. Call connect() first.")

        # Ensure command ends with newline
        if not command.endswith("\n"):
            command += "\n"

        self.socket.sendall(command.encode("ascii"))

    def _receive(self, buffer_size: Optional[int] = None) -> str:
        """
        Receive response from the device.

        Args:
            buffer_size: Size of receive buffer (uses default if None)

        Returns:
            Response string from device
        """
        if buffer_size is None:
            buffer_size = self.buffer_size

        response = b""
        while True:
            try:
                chunk = self.socket.recv(buffer_size)
                if not chunk:
                    break
                response += chunk
                if b"\n" in chunk:
                    break
            except socket.timeout:
                break

        return response.decode("ascii").strip().rstrip("\x00")

    def query(self, command: str) -> str:
        """
        Send a query command and return the response.

        Args:
            command: SCPI query command

        Returns:
            Response string from device
        """
        self._flush_input()  # Clear buffer before query - critical!
        self._send(command)
        time.sleep(0.5)  # Small delay to allow device processing
        return self._receive()

    def get_dut_length(self) -> float:
        """
        Query the Device Under Test (DUT) length.

        Returns:
            DUT length in metres
        """
        response = self.query("CONF:DUTL?")
        return float(response)

    def set_center_wavelength(self, wavelength_nm: float) -> float:
        """
        Set the centre wavelength for measurement.

        Args:
            wavelength_nm: Centre wavelength in nanometres

        Returns:
            Actual set centre wavelength in nanometres
        """
        self._send(f"CONF:CWL {wavelength_nm}")
        time.sleep(0.5)
        response = self.query("CONF:CWL?")
        return float(response)

    def set_wavelength_range(self, range_nm: float) -> float:
        """
        Set the wavelength range for measurement.

        Args:
            range_nm: Wavelength range in nanometres

        Returns:
            Actual set wavelength range in nanometres
        """
        self._send(f"CONF:RANG {range_nm}")
        time.sleep(0.5)
        response = self.query("CONF:RANG?")
        return float(response)

    def set_averaging(self, num_averages: int) -> Tuple[str, str]:
        """
        Enable averaging and set number of averages.

        Args:
            num_averages: Number of averages to perform

        Returns:
            Tuple of (averaging_enabled_status, num_averages_status)
        """
        # Enable averaging
        self._send("CONF:AVGE 1")
        time.sleep(0.5)
        avg_enabled = self.query("CONF:AVGE?")

        # Set number of averages
        self._send(f"CONF:AVGS {num_averages}")
        time.sleep(0.5)
        avg_num = self.query("CONF:AVGS?")

        return avg_enabled, avg_num

    def scan(self, num_averages: int = 1):
        """
        Initiate a measurement scan and wait for completion.

        Args:
            num_averages: Number of averages (affects wait time)

        Raises:
            RuntimeError: If scan encounters an error
        """
        self._send("SCAN")

        # Wait for scan to complete
        time.sleep(0.2 * num_averages)

        # Poll for completion - matching MATLAB implementation
        while True:
            self.query("SYST:ERRD?")  # Query error description
            err_response = self.query("SYST:ERR?")

            # Handle empty or invalid response
            if err_response and err_response.strip():
                try:
                    err_code = int(err_response.strip())
                    if err_code == 0:
                        break
                except ValueError:
                    pass  # Continue polling if conversion fails

            time.sleep(0.1)  # Small delay before retry

    def get_number_of_points(self) -> int:
        """
        Get the number of data points in the measurement.

        Note: The number of points is determined by the OVA based on
        the wavelength range and sample resolution. It cannot be set directly.

        Returns:
            Number of points
        """
        response = self.query("FETC:FSIZ?")
        return int(response)

    def get_sample_resolution(self) -> float:
        """
        Query the current sample resolution of the OVA.

        This is a read-only parameter set by the instrument based on its
        hardware capabilities. The number of points in a scan is determined
        by: N = wavelength_range / sample_resolution

        Returns:
            Sample resolution in nanometres
        """
        response = self.query("CONF:SRES?")
        return float(response)

    def get_wavelength_axis(self) -> np.ndarray:
        """
        Fetch the wavelength axis data.

        Returns:
            Wavelength axis in nanometres
        """
        response = self.query("FETC:XAXI? 0")
        return self._parse_array(response)

    def get_frequency_axis(self) -> np.ndarray:
        """
        Fetch the frequency axis data.

        Returns:
            Frequency axis in terahertz
        """
        response = self.query("FETC:XAXI? 2")
        return self._parse_array(response)

    def get_time_axis(self) -> np.ndarray:
        """
        Fetch the time axis data.

        Returns:
            Time axis in nanoseconds
        """
        response = self.query("FETC:XAXI? 3")
        return self._parse_array(response)

    def get_insertion_loss(self) -> np.ndarray:
        """
        Fetch insertion loss measurement data.

        Returns:
            Insertion loss in decibels
        """
        response = self.query("FETC:MEAS? 0")
        return self._parse_array(response)

    def get_group_delay(self) -> np.ndarray:
        """
        Fetch group delay measurement data.

        Returns:
            Group delay in picoseconds
        """
        response = self.query("FETC:MEAS? 1")
        return self._parse_array(response)

    def get_time_domain_amplitude(self) -> np.ndarray:
        """
        Fetch time domain amplitude data.

        Returns:
            Time domain amplitude in decibels
        """
        response = self.query("FETC:MEAS? 9")
        return self._parse_array(response)

    def get_time_domain_wavelength(self) -> np.ndarray:
        """
        Fetch time domain wavelength data.

        Returns:
            Time domain wavelength in nanometres
        """
        response = self.query("FETC:MEAS? 10")
        return self._parse_array(response)

    def get_linear_phase_deviation(self) -> np.ndarray:
        """
        Fetch linear phase deviation data.

        Returns:
            Linear phase deviation in radians
        """
        response = self.query("FETC:MEAS? 5")
        return self._parse_array(response)

    def _parse_array(self, response: str) -> np.ndarray:
        """
        Parse a comma-separated numeric array response.

        Args:
            response: String containing comma-separated numbers

        Returns:
            NumPy array of values
        """
        # Handle empty response
        if not response or response.strip() == "":
            return np.array([])

        # Parse comma-separated values
        try:
            values = [float(x.strip()) for x in response.split("\r") if x.strip()]
            return np.array(values)
        except ValueError as e:
            raise ValueError(f"Failed to parse array response: {response}. Error: {e}")

    @staticmethod
    def calculate_resolution(axis: np.ndarray) -> float:
        """
        Calculate the resolution (point spacing) of an axis.

        For uniformly-spaced axes, this returns the spacing between adjacent points.
        For non-uniform spacing, this returns the mean spacing.

        Args:
            axis: Array of axis values (wavelength, frequency, or time)

        Returns:
            Resolution (spacing between points)
        """
        if len(axis) < 2:
            return 0.0

        # Calculate differences between adjacent points
        diffs = np.diff(axis)

        # Return mean spacing (for uniform grids, all diffs should be equal)
        return np.mean(np.abs(diffs))

    def get_wavelength_resolution(self) -> float:
        """
        Get the wavelength resolution of the current scan configuration.

        Returns:
            Wavelength resolution in nanometres
        """
        wl_axis = self.get_wavelength_axis()
        return self.calculate_resolution(wl_axis)

    def get_frequency_resolution(self) -> float:
        """
        Get the frequency resolution of the current scan configuration.

        Returns:
            Frequency resolution in terahertz
        """
        f_axis = self.get_frequency_axis()
        return self.calculate_resolution(f_axis)

    def get_time_resolution(self) -> float:
        """
        Get the time domain resolution of the current scan configuration.

        Returns:
            Time resolution in nanoseconds
        """
        t_axis = self.get_time_axis()
        return self.calculate_resolution(t_axis)

    def measure_full(
        self,
        center_wavelength_nm: float,
        wavelength_range_nm: float,
        num_averages: int = 1,
    ) -> Dict[str, np.ndarray]:
        """
        Perform a complete measurement cycle and return all data.

        This method configures the device, performs a scan, and retrieves
        all measurement data in one operation.

        Args:
            center_wavelength_nm: Centre wavelength in nanometres
            wavelength_range_nm: Wavelength range in nanometres
            num_averages: Number of averages

        Returns:
            Dictionary containing all measurement data with keys:
            - 'wl_axis': Wavelength axis (nm)
            - 'f_axis': Frequency axis (THz)
            - 't_axis': Time axis (ns)
            - 'IL': Insertion loss (dB)
            - 'GD': Group delay (ps)
            - 'TD': Time domain amplitude (dB)
            - 'WD': Time domain wavelength (nm)
            - 'LPD': Linear phase deviation (rad)
        """
        # Get DUT length
        dut_length = self.get_dut_length()
        print(f"DUT length: {dut_length} m")

        # Get sample resolution (read-only instrument parameter)
        sample_res = self.get_sample_resolution()
        print(f"Sample resolution: {sample_res:.6f} nm")

        # Configure centre wavelength
        wl_set = self.set_center_wavelength(center_wavelength_nm)
        print(f"Centre wavelength set to: {wl_set} nm")

        # Configure wavelength range
        range_set = self.set_wavelength_range(wavelength_range_nm)
        print(f"Wavelength range set to: {range_set} nm")

        # Configure averaging
        avg_status = self.set_averaging(num_averages)
        print(f"Averaging configured: {avg_status}")

        # Perform scan
        print("Scanning...")
        self.scan(num_averages)

        # Fetch axes
        print("Fetching axes...")
        wl_axis = self.get_wavelength_axis()
        f_axis = self.get_frequency_axis()
        t_axis = self.get_time_axis()

        # Fetch measurement data
        print("Fetching measurement data...")
        IL = self.get_insertion_loss()
        GD = self.get_group_delay()
        TD = self.get_time_domain_amplitude()
        WD = self.get_time_domain_wavelength()
        LPD = self.get_linear_phase_deviation()

        # Calculate resolutions
        wl_res = self.calculate_resolution(wl_axis)
        f_res = self.calculate_resolution(f_axis)
        t_res = self.calculate_resolution(t_axis)

        print(f"Wavelength resolution: {wl_res:.6f} nm")
        print(f"Frequency resolution: {f_res:.6f} THz")
        print(f"Time resolution: {t_res:.6f} ns")

        return {
            "wl_axis": wl_axis,
            "f_axis": f_axis,
            "t_axis": t_axis,
            "IL": IL,
            "GD": GD,
            "TD": TD,
            "WD": WD,
            "LPD": LPD,
            "wl_resolution": wl_res,
            "f_resolution": f_res,
            "t_resolution": t_res,
        }

    def measure_insertion_loss_only(
        self,
        center_wavelength_nm: float,
        wavelength_range_nm: float,
        num_averages: int = 1,
    ) -> np.ndarray:
        """
        Perform a measurement and return only insertion loss data.

        This is a simplified version equivalent to Luna_read_loop.m

        Args:
            center_wavelength_nm: Centre wavelength in nanometres
            wavelength_range_nm: Wavelength range in nanometres
            num_averages: Number of averages

        Returns:
            Insertion loss array in decibels
        """
        # Get DUT length
        dut_length = self.get_dut_length()

        # Configure centre wavelength
        wl_set = self.set_center_wavelength(center_wavelength_nm)

        # Configure wavelength range
        range_set = self.set_wavelength_range(wavelength_range_nm)

        # Configure averaging
        self.set_averaging(num_averages)

        # Perform scan
        self.scan(num_averages)

        # Fetch only insertion loss
        IL = self.get_insertion_loss()

        return IL

    def __enter__(self):
        """Context manager entry - establish connection."""
        self.connect()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit - close connection."""
        self.disconnect()

    def __del__(self):
        """Destructor - ensure connection is closed."""
        self.disconnect()


# Example usage
if __name__ == "__main__":
    # Example 1: Using context manager (recommended)
    with LunaOVA(ip="130.194.137.122") as ova:
        # Perform full measurement
        data = ova.measure_full(
            center_wavelength_nm=1550, wavelength_range_nm=4, num_averages=1
        )

        print(f"Insertion loss shape: {data['IL'].shape}")
        print(
            f"Wavelength range: {data['wl_axis'][0]:.2f} - {data['wl_axis'][-1]:.2f} nm"
        )
