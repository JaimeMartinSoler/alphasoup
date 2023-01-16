
class Way:

    WAY_N = 'N'
    WAY_NE = 'NE'
    WAY_E = 'E'
    WAY_SE = 'SE'
    WAY_S = 'S'
    WAY_SW = 'SW'
    WAY_W = 'W'
    WAY_NW = 'NW'

    WAYS = [WAY_N, WAY_NE, WAY_E, WAY_SE, WAY_S, WAY_SW, WAY_W, WAY_NW]

    def __init__(self, text):
        Way._validate(text)
        self.txt = text

    def __str__(self):
        return self.txt

    @staticmethod
    def _validate(text):
        if not isinstance(text, str):
            raise ValueError(f"text={text} must by type str")
        elif text not in Way.WAYS:
            raise ValueError(f"text={text} must by an allowed str: {Way.WAYS}")

    def is_north_half(self):
        return self.txt in [Way.WAY_N, Way.WAY_NE, Way.WAY_NW]

    def is_south_half(self):
        return self.txt in [Way.WAY_S, Way.WAY_SE, Way.WAY_SW]

    def is_east_half(self):
        return self.txt in [Way.WAY_E, Way.WAY_NE, Way.WAY_SE]

    def is_west_half(self):
        return self.txt in [Way.WAY_W, Way.WAY_NW, Way.WAY_SW]

    def is_straight(self):
        return self.txt in [Way.WAY_N, Way.WAY_E, Way.WAY_S, Way.WAY_W]

    def is_horizontal(self):
        return self.txt in [Way.WAY_E, Way.WAY_W]

    def is_vertical(self):
        return self.txt in [Way.WAY_S, Way.WAY_N]

    def is_diagonal(self):
        return self.txt in [Way.WAY_NE, Way.WAY_SE, Way.WAY_SW, Way.WAY_NW]

    def is_forwards(self):
        return self.txt in [Way.WAY_NE, Way.WAY_E, Way.WAY_SE, Way.WAY_S]

    def is_backwards(self):
        return self.txt in [Way.WAY_SW, Way.WAY_W, Way.WAY_NW, Way.WAY_N]
