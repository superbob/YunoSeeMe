"""
Collection of objects that format profile for output.
Especially:

 * generate JSON output
 * generate PNG output
"""

from abc import ABCMeta, abstractmethod
from io import BytesIO
import json

import numpy as np

import plot_style


class NumpyEncoder(json.JSONEncoder):
    """
    JSONEncoder that for a numpy array generating a simple array
    """
    def default(self, obj):
        """
        if input object is a ndarray it will be converted into an array by calling ndarray.tolist
        """
        if isinstance(obj, np.ndarray):
            return obj.tolist()

        return json.JSONEncoder.default(self, obj)


# TODO need to be tested
class WritableFile:  # pylint: disable=no-init, too-few-public-methods
    """
    The minimal set of required operations for a file-like object
    """
    __metaclass__ = ABCMeta

    @abstractmethod
    def write(self):
        """
        Write operation
        """
        pass


# TODO need to be tested
def is_file_like(obj):
    """
    Checks if the given object is file-like, meaning that it is compatible with the WritableFile class

    :param obj: object to check
    :return: True if the object is file-like, False otherwise
    """
    return isinstance(WritableFile, obj)
    # return hasattr(filename_or_obj, 'write') and callable(filename_or_obj.write)


class ProfileFormat(object):  # pylint: disable=no-init
    """
    Base class to implement to have a functional profile format.
    There is a default implementation for all methods except get_data that needs to be implemented for an instance to
    work entirely.
    """
    def get_data(self, profile_data):  # pylint: disable=unused-argument, no-self-use
        """
        Return the formatted data from the given profile data.
        The default implementation raises an Exception("Not implemented").

        :param profile_data: the profile data to format
        :return: the data
        """
        raise Exception("Not implemented")

    def write_to_filename(self, profile_data, filename):
        """
        Write the profile data to the given filename.
        Opens the file then uses ProfileFormat.write_to_fd to write to it and finally closes it.

        :param profile_data: the profile data to format
        :param filename: the filename to write data to
        :return: None
        """
        fd = open(filename, 'w')  # pylint: disable=invalid-name
        self.write_to_fd(profile_data, fd)
        fd.close()

    def write_to_fd(self, profile_data, fd):  # pylint: disable=invalid-name
        """
        Write the profile data to the given file-like object.

        :param profile_data: the profile data to format
        :param fd: the file-like object to write data to
        :return: None
        """
        fd.write(self.get_data(profile_data))

    def write_to_file(self, profile_data, filename_or_obj):
        """
        Write the profile data to the given filename or file-like object.
        Determines with is_file_like function if the filename_or_obj is a file-like object or a filename.

         * If filename, uses ProfileFormat.write_to_filename
         * If file-like object, uses ProfileFormat.write_to_fd

        :param profile_data: the profile data to format
        :param filename_or_obj: filename or file-like object to write data to
        :return: None
        """
        if is_file_like(filename_or_obj):
            return self.write_to_fd(profile_data, filename_or_obj)

        return self.write_to_filename(profile_data, filename_or_obj)


class JSONProfileFormat(ProfileFormat):
    """
    Profile format that generates JSON
    """
    def get_data(self, profile_data):
        return json.dumps(profile_data, cls=NumpyEncoder)

    def write_to_fd(self, profile_data, fd):
        return json.dump(profile_data, fd, cls=NumpyEncoder)


class PNGProfileFormat(ProfileFormat):
    """
    Profile format that plot a graph in a PNG output
    """

    def __init__(self, style=plot_style.corrected_elevation):
        self.style = style

    def write_to_file(self, profile_data, filename_or_obj):
        self.style(profile_data, filename_or_obj)

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
PNG = PNG_corrected_elevation = PNGProfileFormat()
PNG_curved_sight = PNGProfileFormat(plot_style.curved_sight)
PNG_detailed = PNGProfileFormat(plot_style.detailed_plot)
