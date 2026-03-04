from pygal.style import Style # import custom styling for graph

# function converts rgb tuple into hex code
def rgb2hex(r,g,b):
    return "#{:02x}{:02x}{:02x}".format(r,g,b)

# function that generates single colour for a country based on its value
def styleColours(value,max_value,red,green,blue):
    if max_value == 0:
        return rgb2hex(255, 255, 255)
    # ratio between 0 and 1
    ratio = value / max_value
    # clamp ratio just in case
    ratio = max(0, min(ratio, 1))

    # interpolate from white → selected colour
    r = int(255 + (red - 255) * ratio)
    g = int(255 + (green - 255) * ratio)
    b = int(255 + (blue - 255) * ratio)

    return rgb2hex(r,g,b)

# function that returns a list

