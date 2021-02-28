####################################################################################################
#
# PyResistorColorCode - Python Electronic Tools.
# Copyright (C) 2012 Salvaire Fabrice
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
####################################################################################################
# Fixme: resistor / resistance
"""This modules provides tools to work with resistor colour code and the EIA (Electronics
Industries Association) resistor series values.

The standardised E6, E12, E24, E48, E96 and E192 resistor series values are made available through
an instance of the class :class:`ValuesSeries` named :attr:`E6` and so on.

"""
####################################################################################################
# Source: https://github.com/FabriceSalvaire/PyResistorColorCode/blob/master/PyResistorColorCode/ResistorColourCode.py
# Only needed this one file from the project.


class ValuesSeries(object):

    """This class defines the properties of resistor value series like the standardised E6, E12, E24,
    E48, E96 and E192 resistor series values.

    """

    ##############################################

    def __init__(self, name, number_of_digits, tolerances, values):

        """The parameter *name* gives the name of the series, the parameter *number_of_digits* defines the
        number of digits of the values, the parameter *tolerances* gives the list of tolerances and
        *values* gives the series of values.

        Public attributes:

          :attr:`name`

          :attr:`number_of_digits`

          :attr:`tolerances`

          :attr:`values`

        The name of the series can be retrieved using::

          str(E6)

        The number of values is given by::

          len(E6)

        We can test if a value is in the series using::

          10 in E6

        We can compare two series using the order relation on their number of values, for
        example E6 < E12 is True.

        """

        self.name = name
        self.number_of_digits = number_of_digits
        self.tolerances = tolerances
        self.values = sorted(values)

    ##############################################

    def __str__(self):

        return self.name

    ##############################################

    def __lt__(self, other):

        return len(self) < len(other)

    ##############################################

    def __contains__(self, value):

        return value in self.values

    ##############################################

    def __len__(self):

        return len(self.values)

    ##############################################

    def tolerance_min(self):

        """ Return the minimum tolerance. """

        return min(self.tolerances)

    ##############################################

    def tolerance_max(self):

        """ Return the maximum tolerance. """

        return max(self.tolerances)


####################################################################################################

#: E6 series
E6 = ValuesSeries(name="E6", number_of_digits=2, tolerances=(20,), values=(10, 15, 22, 33, 47, 68))

#: E12 series
E12 = ValuesSeries(name="E12", number_of_digits=2, tolerances=(10,), values=(10, 12, 15, 18, 22, 27, 33, 39, 47, 56, 68, 82))

#: E24 series
E24 = ValuesSeries(
    name="E24",
    number_of_digits=2,
    tolerances=(5, 1),
    values=(10, 12, 15, 18, 22, 27, 33, 39, 47, 56, 68, 82, 11, 13, 16, 20, 24, 30, 36, 43, 51, 62, 75, 91),
)

#: E48 series
E48 = ValuesSeries(
    name="E48",
    number_of_digits=3,
    tolerances=(2,),
    values=(
        100,
        121,
        147,
        178,
        215,
        261,
        316,
        383,
        464,
        562,
        681,
        825,
        105,
        127,
        154,
        187,
        226,
        274,
        332,
        402,
        487,
        590,
        715,
        866,
        110,
        133,
        162,
        196,
        237,
        287,
        348,
        422,
        511,
        619,
        750,
        909,
        115,
        140,
        169,
        205,
        249,
        301,
        365,
        442,
        536,
        649,
        787,
        953,
    ),
)

#: E96 series
E96 = ValuesSeries(
    name="E96",
    number_of_digits=3,
    tolerances=(1,),
    values=(
        100,
        121,
        147,
        178,
        215,
        261,
        316,
        383,
        464,
        562,
        681,
        825,
        102,
        124,
        150,
        182,
        221,
        267,
        324,
        392,
        475,
        576,
        698,
        845,
        105,
        127,
        154,
        187,
        226,
        274,
        332,
        402,
        487,
        590,
        715,
        866,
        107,
        130,
        158,
        191,
        232,
        280,
        340,
        412,
        499,
        604,
        732,
        887,
        110,
        133,
        162,
        196,
        237,
        287,
        348,
        422,
        511,
        619,
        750,
        909,
        113,
        137,
        165,
        200,
        243,
        294,
        357,
        432,
        523,
        634,
        768,
        931,
        115,
        140,
        169,
        205,
        249,
        301,
        365,
        442,
        536,
        649,
        787,
        953,
        118,
        143,
        174,
        210,
        255,
        309,
        374,
        453,
        549,
        665,
        806,
        976,
    ),
)

#: E192 series
E192 = ValuesSeries(
    name="E192",
    number_of_digits=3,
    tolerances=(0.5, 0.25, 0.1),
    values=(
        100,
        121,
        147,
        178,
        215,
        261,
        316,
        383,
        464,
        562,
        681,
        825,
        101,
        123,
        149,
        180,
        218,
        264,
        320,
        388,
        470,
        569,
        690,
        835,
        102,
        124,
        150,
        182,
        221,
        267,
        324,
        392,
        475,
        576,
        698,
        845,
        104,
        126,
        152,
        184,
        223,
        271,
        328,
        397,
        481,
        583,
        706,
        856,
        105,
        127,
        154,
        187,
        226,
        274,
        332,
        402,
        487,
        590,
        715,
        866,
        106,
        129,
        156,
        189,
        229,
        277,
        336,
        407,
        493,
        597,
        723,
        876,
        107,
        130,
        158,
        191,
        232,
        280,
        340,
        412,
        499,
        604,
        732,
        887,
        109,
        132,
        160,
        193,
        234,
        284,
        344,
        417,
        505,
        612,
        741,
        898,
        110,
        133,
        162,
        196,
        237,
        287,
        348,
        422,
        511,
        619,
        750,
        909,
        111,
        135,
        164,
        198,
        240,
        291,
        352,
        427,
        517,
        626,
        759,
        920,
        113,
        137,
        165,
        200,
        243,
        294,
        357,
        432,
        523,
        634,
        768,
        931,
        114,
        138,
        167,
        203,
        246,
        298,
        361,
        437,
        530,
        642,
        777,
        942,
        115,
        140,
        169,
        205,
        249,
        301,
        365,
        442,
        536,
        649,
        787,
        953,
        117,
        142,
        172,
        208,
        252,
        305,
        370,
        448,
        542,
        657,
        796,
        965,
        118,
        143,
        174,
        210,
        255,
        309,
        374,
        453,
        549,
        665,
        806,
        976,
        120,
        145,
        176,
        213,
        258,
        312,
        379,
        459,
        556,
        673,
        816,
        988,
    ),
)

####################################################################################################


def series_iterator(number_of_digits_min=2, number_of_digits_max=3, tolerance_min=1, tolerance_max=5):

    """Return an iterator over the series that match the given constraints on the number of digits
    range and the tolerance ranges.
    """

    for series in E6, E12, E24, E48, E96, E192:
        if (
            number_of_digits_min <= series.number_of_digits <= number_of_digits_max
            and series.tolerance_min() >= tolerance_min
            and series.tolerance_max() <= tolerance_max
        ):
            yield series


####################################################################################################

#: This list defines the ordered set of colours.
# Do not add colors, it will break everything and you will spend hours trying to fix it. See Issue #138
COLOUR_NAMES = (
    "silver",
    "gold",
    "black",
    "brown",
    "red",
    "orange",
    "yellow",
    "green",
    "blue",
    "violet",
    #    "purple",
    "grey",
    #    "gray",
    "white",
)

#: This dictionnary defines for each colour the tolerance values in percent.  Some colours are not assigned.
TOLERANCES = {
    "silver": 10,
    "gold": 5,
    "black": None,
    "brown": 1,
    "red": 2,
    "orange": None,
    "yellow": 5,
    "green": 0.5,
    "blue": 0.25,
    "violet": 0.1,
    "purple": 0.1,
    "grey": 0.05,  # 10 %
    "gray": 0.05,
    "white": None,
    "none": 20,
}


#: This dictionnary defines for each colour the temperature coefficients in ppm/K.  Some colours are not assigned.
TEMPERATURE_COEFFICIENTS = {
    "silver": None,
    "gold": None,
    "black": 250,
    "brown": 100,
    "red": 50,
    "orange": 15,
    "yellow": 25,
    "green": 20,
    "blue": 10,
    "violet": 5,
    "purple": 5,
    "grey": 1,
    "gray": 1,
    "white": None,
}

####################################################################################################


def format_value(x):

    """Return a string representation of a number *x* using the multiplier m, k, M and G, for example
    the number 1230 will be formated as 1.23 k.

    """

    if x < 1:
        return "%g m" % (x * 1e3)
    elif x < 1e3:
        return "%g" % (x)
    elif x < 1e6:
        return "%g k" % (x / 1e3)
    elif x < 1e9:
        return "%g M" % (x / 1e6)
    elif x < 1e12:
        return "%g G" % (x / 1e9)


####################################################################################################


class ColourCode(object):

    """This class defines the meaning of a colour for the digit, the multiplier, the tolerance and
    the temperature coefficient.

    The protocol *repr* is implemented.

    Public attributes:

      :attr:`colour_name`

      :attr:`digit`

      :attr:`multiplier`

      :attr:`tolerance`

      :attr:`temperature_coefficient`

    """

    ##############################################

    def __init__(self, colour_name, digit, multiplier, tolerance, temperature_coefficient):

        self.colour_name = colour_name
        self.digit = digit
        self.multiplier = multiplier
        self.tolerance = tolerance
        self.temperature_coefficient = temperature_coefficient

    ##############################################

    def __repr__(self):

        if self.digit is not None:
            digit_str = "d%u" % self.digit
        else:
            digit_str = ""

        if self.multiplier is not None:
            multiplier_str = "x" + format_value(self.multiplier)
        else:
            multiplier_str = ""

        if self.tolerance is not None:
            tolerance_str = "%.2f %%" % self.tolerance
        else:
            tolerance_str = ""

        if self.temperature_coefficient is not None:
            temperature_coefficient_str = "%u ppm" % self.temperature_coefficient
        else:
            temperature_coefficient_str = ""

        return "%-6s: " % self.colour_name + ", ".join(
            x for x in (digit_str, multiplier_str, tolerance_str, temperature_coefficient_str) if x
        )


####################################################################################################

#: This dictionnary maps the colour name and their :class:`ColourCode` instance.
COLOUR_CODES = {}
for i, colour_name in enumerate(COLOUR_NAMES):
    digit = i - 2
    multiplier = 10 ** digit
    # digit is defined positive
    if digit < 0:
        digit = None
    COLOUR_CODES[colour_name] = ColourCode(
        colour_name, digit, multiplier, TOLERANCES[colour_name], TEMPERATURE_COEFFICIENTS[colour_name]
    )

####################################################################################################


class Resistor(object):

    """This class represents a resitor.

    Public attributes:

      :attr:`value`

      :attr:`number_of_digits`

      :attr:`digit1`

      :attr:`digit2`

      :attr:`digit3`

      :attr:`multiplier`

      :attr:`digit1_colour`

      :attr:`digit2_colour`

      :attr:`digit3_colour`

      :attr:`multiplier_colour`

      :attr:`significant_digits`
        The resitor values is equal to significant_digits * multiplier.

      :attr:`series`

    """

    ##############################################

    def __init__(
        self,
        value=None,
        number_of_digits=None,
        digit1=0,
        digit2=0,
        digit3=None,
        multiplier=None,
        tolerance=None,
        temperature_coefficient=None,
    ):

        if value is not None:
            self.value = value
            self.number_of_digits = number_of_digits
            # Not implemented
            self.digit1 = None
            self.digit2 = None
            self.digit3 = None
            self.multiplier = None
            self.digit1_colour = None
            self.digit2_colour = None
            self.digit3_colour = None
            self.multiplier_colour = None
            self.significant_digits = None
        else:
            self.digit1_colour = digit1
            self.digit2_colour = digit2
            self.digit3_colour = digit3
            self.multiplier_colour = multiplier
            self._compute_value_from_colours()

        self._init_tolerance(tolerance)
        self._init_temperature_coefficient(temperature_coefficient)
        self.series = self._guess_series()

    ##############################################

    def _init_tolerance(self, tolerance):

        """Set the tolerance from a colour or a real number."""

        if tolerance is None:
            self.tolerance = None
            self.tolerance_colour = None
        else:
            try:
                self.tolerance = COLOUR_CODES[tolerance].tolerance
                self.tolerance_colour = tolerance
            except KeyError:
                self.tolerance = float(tolerance)

    ##############################################

    def _init_temperature_coefficient(self, temperature_coefficient):

        """Set the temperature coefficient from a colour or a real number."""

        if temperature_coefficient is None:
            self.temperature_coefficient = None
            self.temperature_coefficient_colour = None
        else:
            try:
                self.temperature_coefficient = COLOUR_CODES[temperature_coefficient].temperature_coefficient
                self.temperature_coefficient_colour = temperature_coefficient
            except KeyError:
                self.temperature_coefficient = float(temperature_coefficient)

    ##############################################

    def _compute_value_from_colours(self):

        """compute the resistance value from the colour code."""

        try:
            self.digit1 = COLOUR_CODES[self.digit1_colour].digit
            self.digit2 = COLOUR_CODES[self.digit2_colour].digit
        except Exception:
            raise ValueError("Forbidden digit")
        self.multiplier = COLOUR_CODES[self.multiplier_colour].multiplier
        self.significant_digits = self.digit1 * 10 + self.digit2
        if self.digit3_colour is not None:
            self.digit3 = COLOUR_CODES[self.digit3_colour].digit
            self.significant_digits = self.significant_digits * 10 + self.digit3
            self.number_of_digits = 3
        else:
            self.number_of_digits = 2
        self.value = self.significant_digits * self.multiplier

    ##############################################

    def _guess_series(self):

        """Guess the series of the resistor.


        Return the lowest series that match the resistor properties else :obj:`None`.

        """

        if self.number_of_digits is not None:
            if self.number_of_digits == 2:
                list_of_series = (E6, E12, E24)
            else:
                list_of_series = (E48, E96, E192)
        else:
            list_of_series = (E6, E12, E24, E48, E96, E192)

        resitor_series = None
        for series in list_of_series:
            # print '  ', self.significant_digits, self.tolerance, series.name, series.tolerances
            if resitor_series is not None:
                break
            if self.significant_digits in series:
                if self.tolerance is None:
                    resitor_series = series
                else:
                    if self.tolerance in series.tolerances:
                        resitor_series = series

        return resitor_series

    ##############################################

    def value_range(self):

        """Return the resistance range according to the resistance tolerance."""

        if self.tolerance is not None:
            return tuple([self.value * (1 + sign * self.tolerance / 100.0) for sign in (-1, 1)])
        else:
            return None

    ##############################################

    def __str__(self):

        if self.tolerance is not None:
            tolerance_str = "%.2f%%" % self.tolerance
        else:
            tolerance_str = ""

        if self.temperature_coefficient is not None:
            temperature_coefficient_str = "%u ppm" % self.temperature_coefficient
        else:
            temperature_coefficient_str = ""

        series_name = str(self.series)

        return " ".join(
            x
            for x in (
                "%sΩ" % (format_value(self.value),),
                tolerance_str,
                temperature_coefficient_str,
                "%s series" % series_name,
            )
            if x
        )

    ##############################################

    def digit_colour_iterator(self):

        """Return a iterator over the colours of the resistance value."""

        return iter(
            [
                digit
                for digit in (self.digit1_colour, self.digit2_colour, self.digit3_colour, self.multiplier_colour)
                if digit is not None
            ]
        )


####################################################################################################


class ResistorDecoder(object):

    """This class implements a resistor decoder using an inference algorithm:

    * The given list of colours doesn't require to be oriented (code polarity), both orientation
      Right-Left and Left-Right are tested (bidirectional inference),

    * At least three colours must be provided (two digits colour and the multiplier colour),

    * The colours are interpreted by priority as resistance value, then tolerance and finally
      temperature coefficient.

    * The resistance value must exists in a series and its tolerance must be defined if there is a
      colour assigned to it.

    """

    ##############################################

    def _append_hypothesis(self, resistor_configuration, hypotheses):

        """Append an hypothesis if it is acceptable."""

        # print 'Try:', keys
        try:
            resistor = Resistor(**resistor_configuration)
            # print resistor.value, resistor.series
            # Resistor value must exists in a series and
            # its tolerance must be defined if there is a colour assigned to it
            if (
                resistor.series is not None
                and not (resistor.tolerance_colour is not None and resistor.tolerance is None)
                and
                # remove doublon for symetric cases
                resistor.value not in [x.value for x in hypotheses]
            ):
                hypotheses.append(resistor)
        except Exception:
            # raise
            pass

    ##############################################

    def _decode(self, colour_names, hypotheses):

        """Decode a resistor in one direction from the given list of colour *colour_names*."""

        two_digits_bands = ["digit1", "digit2", "multiplier"]
        three_digits_bands = ["digit1", "digit2", "digit3", "multiplier"]

        number_of_colours = len(colour_names)
        if number_of_colours == 3:
            configurations = (two_digits_bands,)
        elif number_of_colours == 4:
            configurations = (two_digits_bands + ["tolerance"], three_digits_bands)
        elif number_of_colours == 5:
            configurations = (
                two_digits_bands + ["tolerance", "temperature_coefficient"],
                three_digits_bands + ["tolerance"],
            )
        elif number_of_colours == 6:
            configurations = (three_digits_bands + ["tolerance", "temperature_coefficient"],)

        for band_configuration in configurations:
            resistor_configuration = {band: colour_names[i] for i, band in enumerate(band_configuration)}
            self._append_hypothesis(resistor_configuration, hypotheses)

    ##############################################

    def decode(self, colour_names):

        """Decode a resistor from the given list of colour *colour_names*."""

        number_of_colours = len(colour_names)
        if number_of_colours < 3:
            raise ValueError("Too few bands")
        elif number_of_colours > 6:
            raise ValueError("Too many bands")

        hypotheses = []
        self._decode(colour_names, hypotheses)
        self._decode(list(reversed(colour_names)), hypotheses)

        return hypotheses
