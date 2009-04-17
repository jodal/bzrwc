import math

def pretty_max_number(value, base=10):
    spacing = get_spacing(value, base)

    if spacing <= 1:
        return base

    return spacing * math.ceil(value/spacing)

def get_spacing(value, base=10):
    if value <= 0:
        return 1

    unit = base**(math.floor(math.log(value, base)))

    if value/float(unit) < 5:
        unit /= 5
    if value/float(unit) > 8:
        unit *= 4

    return unit
