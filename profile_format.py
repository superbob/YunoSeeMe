"""
Collection of objects that format profile for output.
Especially:

 * generate JSON output
 * generate PNG output
"""

from abc import ABCMeta, abstractmethod
from io import BytesIO
import math
import json

import numpy as np
import matplotlib.pyplot as plt


class NumpyEncoder(json.JSONEncoder):
    def default(self, obj):
        """
        if input object is a ndarray it will be converted into an array by calling ndarray.tolist
        """
        if isinstance(obj, np.ndarray):
            return obj.tolist()

        return json.JSONEncoder.default(self, obj)


def manual_linear_scaled_range(data):
    data_min = np.amin(data)
    data_max = np.amax(data)

    log_diff = math.log10(data_max - data_min)
    step = 10 ** math.floor(log_diff)

    scaled_min = math.floor(data_min / step) * step
    scaled_max = math.ceil(data_max / step) * step

    return scaled_min, scaled_max


def generate_figure(profile_data, filename, file_format='png'):
    # Prepare data
    x = profile_data['distances'] / 1000
    y_elev_plus_correction = profile_data['elevations'] + profile_data['overheads']
    y_sight = profile_data['sights']

    y_min, y_max = manual_linear_scaled_range(np.concatenate([y_elev_plus_correction, y_sight]))
    floor = np.full_like(x, y_min)
    floor_plus_correction = floor + profile_data['overheads']

    # Prepare plot
    fig = plt.figure()
    sub_plt = fig.add_subplot(111)

    # Plot
    sub_plt.plot(x, y_sight, 'g-', label='Sight', linewidth=0.5)

    sub_plt.fill_between(x, y_elev_plus_correction, floor_plus_correction, linewidth=0, facecolor=(0.7, 0.7, 0.7))
    sub_plt.fill_between(x, floor_plus_correction, floor, linewidth=0, facecolor=(0.85, 0.85, 0.7))

    # Fix limits
    sub_plt.set_xlim(min(x), max(x))
    sub_plt.set_ylim(y_min, y_max)

    # Style
    sub_plt.set_title("Elevation (m) vs. Distance (km)")

    sub_plt.spines["top"].set_visible(False)
    sub_plt.spines["bottom"].set_visible(False)
    sub_plt.spines["right"].set_visible(False)
    sub_plt.spines["left"].set_visible(False)

    sub_plt.tick_params(axis='both', which='both', bottom='on', top='off',
                        labelbottom='on', left='off', right='off', labelleft='on')

    sub_plt.grid(axis='y')

    # Format and save
    # setting dpi with figure.set_dpi() seem to be useless, the dpi really used is the one in savefig()
    fig.set_size_inches(10, 3.5)
    fig.savefig(filename, bbox_inches='tight', dpi=80, format=file_format)


# TODO need to be tested
class WritableFile:
    __metaclass__ = ABCMeta

    @abstractmethod
    def write(self):
        pass


# TODO need to be tested
def is_file_like(filename_or_obj):
    return isinstance(WritableFile, filename_or_obj)
    # return hasattr(filename_or_obj, 'write') and callable(filename_or_obj.write)


class ProfileFormat:
    """
    Base class to implement to have a functional profile format.
    There is a default implementation for all methods except get_data that needs to be implemented for an instance to
    work entirely.
    """
    def get_data(self, profile_data):
        raise Exception("Not implemented")

    def write_to_filename(self, profile_data, filename):
        fd = open(filename, 'w')
        self.write_to_fd(profile_data, fd)
        fd.close()

    def write_to_fd(self, profile_data, fd):
        fd.write(self.get_data(profile_data))

    def write_to_file(self, profile_data, filename_or_obj):
        if is_file_like(filename_or_obj):
            return self.write_to_fd(profile_data, filename_or_obj)

        return self.write_to_filename(profile_data, filename_or_obj)


class JSONProfileFormat(ProfileFormat):
    def get_data(self, profile_data):
        return json.dumps(profile_data, cls=NumpyEncoder)

    def write_to_fd(self, profile_data, fd):
        return json.dump(profile_data, fd, cls=NumpyEncoder)


class PNGProfileFormat(ProfileFormat):
    def write_to_file(self, profile_data, filename_or_obj):
        generate_figure(profile_data, filename_or_obj)

    def write_to_filename(self, profile_data, filename):
        self.write_to_file(profile_data, filename)

    def write_to_fd(self, profile_data, fd):
        self.write_to_file(profile_data, fd)

    def get_data(self, profile_data):
        buf = BytesIO()
        self.write_to_fd(profile_data, buf)
        buf.seek(0)
        return buf


JSON = JSONProfileFormat()
PNG = PNGProfileFormat()
