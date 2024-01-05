def bytes_to_rgb(data):
    # Convert the received bytearray data to a list of RGB tuples
    rgb_data = []
    for i in range(0, len(data), 3):
        rgb_data.append((data[i], data[i+1], data[i+2]))
    return rgb_data  # Should return a list of (R, G, B) tuples