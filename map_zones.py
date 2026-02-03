def get_lol_location(x, y, inverted_y=True):
    MAP_SIZE = 15000

    if x is None or y is None:
        return "UNKNOWN"

    if inverted_y:
        y = MAP_SIZE - y

    # Bases
    if x < 3000 and y < 3000:
        return "BLUE_BASE"
    if x > 12000 and y > 12000:
        return "RED_BASE"

    # River (diagonal)
    # The river follows the line where x + y is roughly the map size
    if abs(x + y - MAP_SIZE) < 1200:
        return "RIVER"

    # Mid Lane (diagonal)
    # Follows the line where x equals y
    if abs(x - y) < 1200:
        return "MID_LANE"

    # Top Lane (Top-Left edge)
    if (x < 2500 and y > 5000) or (y > 12500 and x < 10000):
        return "TOP_LANE"

    # Bot Lane (Bottom-Right edge)
    if (x > 12500 and y < 10000) or (y < 2500 and x > 5000):
        return "BOT_LANE"

    return "JUNGLE"
