import serial.tools.list_ports

def extract_tuple_properties(port_tuple):
    """
    Extracts known properties from a tuple-based port.

    :param port_tuple: The tuple-based serial port to check.
    :return: A dictionary with extracted properties.
    """
    device, description, hwid = port_tuple
    properties = {
        'device': device,
        'description': description,
        'hwid': hwid,
    }
    
    # Extract VID and PID from hwid string, typically formatted as "USB VID:PID=2341:0043"
    if 'USB VID:PID=' in hwid:
        vid_pid_part = hwid.split('USB VID:PID=')[1]
        vid, pid = vid_pid_part.split(':')[:2]
        properties['vid'] = int(vid, 16)
        properties['pid'] = int(pid, 16)
    
    # Extract serial number if available in hwid string
    if 'SER=' in hwid:
        serial_part = hwid.split('SER=')[1]
        serial_number = serial_part.split()[0]
        properties['serial_number'] = serial_number
    
    return properties

def test_port_tuple(port_tuple, signature):
    """
    Check if a tuple-based serial port matches all given criteria.
    
    :param port_tuple: The tuple-based serial port to check.
    :param signature: Dictionary of properties and acceptable values.
    :return: True if the port matches all criteria, False otherwise.
    """
    port_properties = extract_tuple_properties(port_tuple)
    
    for key, values in signature.items():
        if key in port_properties:
            if all(value not in [port_properties[key]] for value in values):
                return False
        else:
            return False
    return True

def test_port_object(port, signature):
    """
    Check if an object-based serial port matches all given criteria.
    
    :param port: The object-based serial port to check.
    :param signature: Dictionary of properties and acceptable values.
    :return: True if the port matches all criteria, False otherwise.
    """
    for key, values in signature.items():
        port_value = getattr(port, key, None)
        if port_value not in values:
            return False
    return True

def get_device(port):
    """
    Extract the device path from the port information.
    
    :param port: The serial port information.
    :return: The device path (e.g., /dev/ttyACM0).
    """
    if isinstance(port, tuple):
        return port[0]
    return port.device

def find_port(signature):
    """
    Find a serial port that matches given criteria.
    
    :param signature: Dictionary containing serial port properties and lists of acceptable values.
    :return: The device port if found, otherwise None.
    """
    for port in serial.tools.list_ports.comports():
        if isinstance(port, tuple):
            if test_port_tuple(port, signature):
                return get_device(port)
        else:
            if test_port_object(port, signature):
                return get_device(port)
    return None

# Example usage:
# signature = {
#     'vid': [0x2341],  # List of acceptable Vendor IDs
#     'pid': [0x0043],  # List of acceptable Product IDs
#     'manufacturer': ['Arduino (www.arduino.cc)'],  # Example of another property
#     'serial_number': ['85730303031351B0C1B1']  # Example serial number
# }
# device = find_port(signature)
# if device:
#     print(f"Found device: {device}")
# else:
#     print("Device not found")