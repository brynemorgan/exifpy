"""
Misc utilities.
"""

from fractions import Fraction


def ord_(dta):
    if isinstance(dta, str):
        return ord(dta)
    return dta


def get_gps_coords(tags: dict) -> tuple:

    lng_ref_tag_name = 'GPS GPSLongitudeRef'
    lng_tag_name = 'GPS GPSLongitude'
    lat_ref_tag_name = 'GPS GPSLatitudeRef'
    lat_tag_name = 'GPS GPSLatitude'

    # Check if these tags are present
    gps_tags = [lng_ref_tag_name, lng_tag_name, lat_tag_name, lat_tag_name]
    for tag in gps_tags:
        if not tag in tags.keys():
            return ()

    lng_ref_val = tags[lng_ref_tag_name].values
    lng_coord_val = [c.decimal() for c in tags[lng_tag_name].values]

    lat_ref_val = tags[lat_ref_tag_name].values
    lat_coord_val = [c.decimal() for c in tags[lat_tag_name].values]

    lng_coord = sum([c/60**i for i, c in enumerate(lng_coord_val)])
    lng_coord *= (-1) ** (lng_ref_val == 'W')

    lat_coord = sum([c/60**i for i, c in enumerate(lat_coord_val)])
    lat_coord *= (-1) ** (lat_ref_val == 'S')

    return (lat_coord, lng_coord)


def dms_to_dd(dms):
    """
    Converts coordinate value from degrees, minutes, seconds to decimal degrees.

    Parameters
    ----------
    dms : list
        List of the form [deg, min, sec].

    Returns
    -------
    dd : float
        Coordinate in decimal degrees.
    """
    dd = dms[0] + float(dms[1])/60 + float(dms[2])/3600

    return dd

class Ratio(Fraction):
    """
    Ratio object that eventually will be able to reduce itself to lowest
    common denominator for printing.
    """

    # We're immutable, so use __new__ not __init__
    def __new__(cls, numerator=0, denominator=None):
        try:
            self = super(Ratio, cls).__new__(cls, numerator, denominator)
        except ZeroDivisionError:
            self = super(Ratio, cls).__new__(cls)
            self._numerator = numerator
            self._denominator = denominator
        return self

    def __repr__(self) -> str:
        return str(self)

    @property
    def num(self):
        return self.numerator

    @property
    def den(self):
        return self.denominator

    def decimal(self) -> float:
        return float(self)
