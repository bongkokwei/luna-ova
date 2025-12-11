# Luna OVA Python Interface

A Python interface for controlling Luna Optical Vector Analyzer (OVA) instruments via TCP/IP connection. This library provides a Pythonic wrapper around the SCPI commands used to configure and acquire measurements from Luna OVA devices.

## Overview

The Luna OVA is an optical testing instrument that performs comprehensive characterisation of fibre optic components, modules, and subsystems. It measures the complete transfer function including insertion loss, group delay, chromatic dispersion, and phase information across a wavelength range.

This Python class replicates the functionality from the original MATLAB implementation whilst providing a more modern, type-annotated interface.

## Features

- TCP/IP connection management with automatic reconnection handling
- Configuration of measurement parameters (wavelength, range, averaging)
- Scan control and data acquisition
- Support for multiple measurement types:
  - Insertion Loss (IL)
  - Group Delay (GD)
  - Time Domain amplitude (TD)
  - Wavelength Distribution (WD)
  - Linear Phase Deviation (LPD)
- Type hints for improved IDE support
- NumPy integration for efficient data handling

## Installation

### Requirements

- Python 3.7+
- NumPy
- Network access to Luna OVA device

### Install Dependencies

```bash
pip install numpy
```

### Import the Class

```python
from luna_ova import LunaOVA
```

## Quick Start

```python
from luna_ova import LunaOVA
import matplotlib.pyplot as plt

# Initialize connection
ova = LunaOVA(ip='130.194.137.137')

# Connect to device
ova.connect()

# Configure measurement
ova.set_center_wavelength(1550)  # Centre wavelength in nm
ova.set_wavelength_range(40)     # Range in nm
ova.set_averaging(5)              # Number of averages

# Perform scan
ova.scan(num_averages=5)

# Retrieve data
wavelength = ova.get_wavelength_axis()
insertion_loss = ova.get_insertion_loss()

# Plot results
plt.plot(wavelength, insertion_loss)
plt.xlabel('Wavelength (nm)')
plt.ylabel('Insertion Loss (dB)')
plt.show()

# Disconnect
ova.disconnect()
```

## API Reference

### Initialisation

#### `LunaOVA(ip, port, timeout, buffer_size)`

Initialise a Luna OVA connection object.

**Parameters:**
- `ip` (str, optional): IP address of the Luna OVA device. Default: `'130.194.137.137'`
- `port` (int, optional): TCP port for communication. Default: `1`
- `timeout` (float, optional): Socket timeout in seconds. Default: `0.1`
- `buffer_size` (int, optional): Size of I/O buffers. Default: `524288` (2¹⁹ bytes)

**Example:**
```python
ova = LunaOVA(ip='192.168.1.100', timeout=0.5)
```

---

### Connection Management

#### `connect() -> str`

Establish TCP/IP connection to the Luna OVA device.

**Returns:**
- `str`: Device identification string

**Raises:**
- `ConnectionError`: If connection fails

**Example:**
```python
device_id = ova.connect()
print(f"Connected to: {device_id}")
```

#### `disconnect()`

Close the connection to the Luna OVA device.

**Example:**
```python
ova.disconnect()
```

---

### Configuration Methods

#### `get_dut_length() -> float`

Query the Device Under Test (DUT) length as determined by the OVA.

**Returns:**
- `float`: DUT length in metres

**Example:**
```python
length = ova.get_dut_length()
print(f"DUT length: {length} m")
```

#### `set_center_wavelength(wavelength_nm) -> float`

Set the centre wavelength for measurement.

**Parameters:**
- `wavelength_nm` (float): Centre wavelength in nanometres

**Returns:**
- `float`: Actual set centre wavelength in nanometres (may differ slightly from requested)

**Example:**
```python
actual_wavelength = ova.set_center_wavelength(1550.0)
```

#### `set_wavelength_range(range_nm) -> float`

Set the wavelength range for measurement.

**Parameters:**
- `range_nm` (float): Wavelength range in nanometres

**Returns:**
- `float`: Actual set wavelength range in nanometres

**Example:**
```python
actual_range = ova.set_wavelength_range(40.0)
```

#### `set_averaging(num_averages) -> Tuple[str, str]`

Enable averaging and set the number of averages.

**Parameters:**
- `num_averages` (int): Number of averages to perform

**Returns:**
- `Tuple[str, str]`: Tuple of (averaging_enabled_status, num_averages_status)

**Example:**
```python
avg_enabled, avg_num = ova.set_averaging(10)
```

#### `get_sample_resolution() -> float`

Query the current sample resolution of the OVA.

This is a read-only parameter determined by the instrument hardware. The number of points in a scan is calculated as:

$$N = \frac{\text{wavelength range}}{\text{sample resolution}}$$

**Returns:**
- `float`: Sample resolution in nanometres

**Example:**
```python
resolution = ova.get_sample_resolution()
print(f"Sample resolution: {resolution} nm")
```

---

### Measurement Methods

#### `scan(num_averages)`

Initiate a measurement scan and wait for completion.

**Parameters:**
- `num_averages` (int, optional): Number of averages (affects wait time). Default: `1`

**Raises:**
- `RuntimeError`: If scan encounters an error

**Example:**
```python
ova.scan(num_averages=5)
```

#### `get_number_of_points() -> int`

Get the number of data points in the measurement.

**Note:** The number of points is determined by the OVA based on wavelength range and sample resolution. It cannot be set directly.

**Returns:**
- `int`: Number of points

**Example:**
```python
num_points = ova.get_number_of_points()
```

---

### Data Retrieval Methods

#### `get_wavelength_axis() -> np.ndarray`

Fetch the wavelength axis data.

**Returns:**
- `np.ndarray`: Wavelength values in nanometres

**Example:**
```python
wavelengths = ova.get_wavelength_axis()
```

#### `get_frequency_axis() -> np.ndarray`

Fetch the frequency axis data.

**Returns:**
- `np.ndarray`: Frequency values in terahertz

**Example:**
```python
frequencies = ova.get_frequency_axis()
```

#### `get_time_axis() -> np.ndarray`

Fetch the time axis data for time-domain measurements.

**Returns:**
- `np.ndarray`: Time values in nanoseconds

**Example:**
```python
time = ova.get_time_axis()
```

#### `get_insertion_loss() -> np.ndarray`

Fetch insertion loss measurement data.

**Returns:**
- `np.ndarray`: Insertion loss in decibels

**Example:**
```python
il = ova.get_insertion_loss()
```

#### `get_group_delay() -> np.ndarray`

Fetch group delay measurement data.

**Returns:**
- `np.ndarray`: Group delay in picoseconds

**Example:**
```python
gd = ova.get_group_delay()
```

#### `get_time_domain_amplitude() -> np.ndarray`

Fetch time-domain amplitude data.

**Returns:**
- `np.ndarray`: Time-domain amplitude in decibels

**Example:**
```python
td_amp = ova.get_time_domain_amplitude()
```

#### `get_time_domain_wavelength() -> np.ndarray`

Fetch time-domain wavelength distribution.

**Returns:**
- `np.ndarray`: Wavelength values in nanometres

**Example:**
```python
td_wl = ova.get_time_domain_wavelength()
```

#### `get_linear_phase_deviation() -> np.ndarray`

Fetch linear phase deviation data.

**Returns:**
- `np.ndarray`: Linear phase deviation in radians

**Example:**
```python
lpd = ova.get_linear_phase_deviation()
```

---

### Low-Level Methods

#### `query(command) -> str`

Send a SCPI query command and return the response.

**Parameters:**
- `command` (str): SCPI query command

**Returns:**
- `str`: Response string from device

**Example:**
```python
response = ova.query('*IDN?')
```

---

## Complete Example

Here's a comprehensive example demonstrating a typical measurement workflow:

```python
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
    ova = LunaOVA(ip='130.194.137.137')
    
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
        
        axes[0].plot(wavelength, il, 'b-', linewidth=1)
        axes[0].set_xlabel('Wavelength (nm)')
        axes[0].set_ylabel('Insertion Loss (dB)')
        axes[0].set_title('Insertion Loss')
        axes[0].grid(True, alpha=0.3)
        
        axes[1].plot(wavelength, gd, 'r-', linewidth=1)
        axes[1].set_xlabel('Wavelength (nm)')
        axes[1].set_ylabel('Group Delay (ps)')
        axes[1].set_title('Group Delay')
        axes[1].grid(True, alpha=0.3)
        
        axes[2].plot(wavelength, lpd, 'g-', linewidth=1)
        axes[2].set_xlabel('Wavelength (nm)')
        axes[2].set_ylabel('Linear Phase Deviation (rad)')
        axes[2].set_title('Linear Phase Deviation')
        axes[2].grid(True, alpha=0.3)
        
        plt.tight_layout()
        plt.savefig('ova_measurement.png', dpi=300)
        print("\nPlot saved as 'ova_measurement.png'")
        
        return wavelength, il, gd, lpd
        
    finally:
        # Always disconnect
        ova.disconnect()
        print("\nDisconnected from Luna OVA")

if __name__ == '__main__':
    wavelength, il, gd, lpd = measure_device(centre_wl=1550, wl_range=40, averages=5)
```

## SCPI Commands Reference

The Luna OVA uses Standard Commands for Programmable Instruments (SCPI). Common commands used by this class:

| Command | Description | Unit |
|---------|-------------|------|
| `*IDN?` | Device identification | - |
| `CONF:DUTL?` | Query DUT length | metres |
| `CONF:CWL` | Set centre wavelength | nanometres |
| `CONF:CWL?` | Query centre wavelength | nanometres |
| `CONF:RANG` | Set wavelength range | nanometres |
| `CONF:RANG?` | Query wavelength range | nanometres |
| `CONF:AVGE` | Enable/disable averaging | boolean |
| `CONF:AVGS` | Set number of averages | integer |
| `CONF:SRES?` | Query sample resolution | nanometres |
| `SCAN` | Initiate measurement scan | - |
| `FETC:FSIZ?` | Query number of data points | integer |
| `FETC:XAXI? 0` | Fetch wavelength axis | nanometres |
| `FETC:XAXI? 2` | Fetch frequency axis | terahertz |
| `FETC:XAXI? 3` | Fetch time axis | nanoseconds |
| `FETC:MEAS? 0` | Fetch insertion loss | decibels |
| `FETC:MEAS? 1` | Fetch group delay | picoseconds |
| `FETC:MEAS? 5` | Fetch linear phase deviation | radians |
| `FETC:MEAS? 9` | Fetch time-domain amplitude | decibels |
| `FETC:MEAS? 10` | Fetch time-domain wavelength | nanometres |

For complete SCPI command reference, refer to the Luna OVA User Guide.

## Error Handling

The class includes error handling for common issues:

```python
from luna_ova import LunaOVA

ova = LunaOVA(ip='192.168.1.100')

try:
    ova.connect()
    ova.scan()
except ConnectionError as e:
    print(f"Connection failed: {e}")
except RuntimeError as e:
    print(f"Operation failed: {e}")
finally:
    ova.disconnect()
```

## Troubleshooting

### Connection Issues

**Problem:** `ConnectionError: Failed to connect to Luna OVA`

**Solutions:**
- Verify the IP address is correct
- Ensure the device is powered on and network-accessible
- Check firewall settings
- Verify no other application is using the connection

### Timeout Errors

**Problem:** Socket timeout during data retrieval

**Solutions:**
- Increase timeout value: `LunaOVA(timeout=1.0)`
- Reduce number of averages
- Check network stability

### No Data After Scan

**Problem:** Data arrays are empty after `get_*()` calls

**Solutions:**
- Ensure `scan()` completed successfully
- Verify device is properly calibrated (see User Guide)
- Check error status with `query('SYST:ERR?')`

## Comparison with MATLAB Version

Key differences from the original MATLAB implementation:

| Feature | MATLAB | Python |
|---------|--------|--------|
| Connection | `instrfind`, `tcpip` | Native `socket` |
| Data types | Cell arrays | NumPy arrays |
| Type hints | None | Full type annotations |
| Error handling | Basic | Enhanced with exceptions |
| Buffer flushing | Explicit `flushinput` | Automatic |
| Method naming | camelCase | snake_case (PEP 8) |

## Specifications

### Luna OVA Device

- **Wavelength ranges:** 1265–1335 nm or 1525–1610 nm
- **Maximum output power:** 2.4 mW
- **Laser classification:** Class 1 Laser Product (IEC 60825-1:2007)
- **Connection:** TCP/IP via Ethernet
- **Default port:** 1

### Network Requirements

- TCP/IP connectivity
- Default IP: 130.194.137.137 (configurable)
- Port: 1
- Recommended buffer size: 524288 bytes (2¹⁹)

## License

This code is converted from the original MATLAB implementation. Refer to your Luna OVA device licence and documentation for usage terms.

## References

- Luna Technologies OVA User Guide (OVA+OFDR-UG22-04-11-11)
- Software version: OVA-sw5.2, OFDR-sw4.1
- SCPI Standard: IEEE 488.2

## Support

For device-specific issues, consult the Luna OVA User Guide or contact Luna Technologies support.

For issues with this Python implementation, check:
1. Network connectivity to device
2. Correct IP address configuration
3. Device calibration status
4. Python dependencies installed correctly

---

**Note:** This implementation assumes the Luna OVA is properly calibrated and configured through its native software before use with this Python interface. Calibration procedures should be performed according to the User Guide.
