class Value:
    def __init__(self, value, units):
        self.value = value
        self.units = units

    def get(self, units, whole=None, get_as_int=True):
        if units == self.units:
            return self.value
        # Convert
        if whole is None:
            raise AttributeError(f'Cannot convert between units when "whole" parameter not provided')
        if self.value > whole:
            raise AttributeError(f'Value > 100%')
        if units == '%':
            ret = 100 * self.value / whole
        else:
            ret = (self.value * whole) / 100
        return int(ret) if get_as_int else ret

class Area:
    def __init__(self, x, y, w, h, units='%'):
        self.x = Value(x, units)
        self.y = Value(y, units)
        self.w = Value(w, units)
        self.h = Value(h, units)

    def get(self, units, height=None, width=None):
        x = self.x.get(units, width)
        w = self.w.get(units, width)
        y = self.y.get(units, height)
        h = self.h.get(units, height)
        if units == '%':
            if (x + w > 100) or (y + h > 100):
                raise ValueError('Rectangle area is out of bounds')
        else:
            if (x + w > width) or (y + h > height):
                raise ValueError('Rectangle area is out of bounds')
        return (x, y, w, h)

    @property
    def height(self):
        return self.h.get(units='pixel')

    @property
    def width(self):
        return self.w.get(units='pixel')

