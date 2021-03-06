"""Define the File Type.

The primary purpose of the File object is to track the protocol to be used
to transfer the file as well as to give the appropriate filepath depending
on where(client-side, remote-side, intermediary-side) the File.filepath is
being called from
"""

import os
import logging
from urllib.parse import urlparse
from parsl.data_provider.data_manager import DataManager


logger = logging.getLogger(__name__)


class File(object):
    """The Parsl File Class.

    This is planned to be a very simple class that simply
    captures various attributes of a file, and relies on client-side and worker-side
    systems to enable to appropriate transfer of files.
    """

    def __init__(self, url, dman=None, cache=False, caching_dir=".", staging='direct'):
        """Construct a File object from a url string.

        Args:
           - url (string) : url string of the file e.g.
              - 'input.txt'
              - 'file:///scratch/proj101/input.txt'
              - 'globus://go#ep1/~/data/input.txt'
              - 'globus://ddb59aef-6d04-11e5-ba46-22000b92c6ec/home/johndoe/data/input.txt'
           - dman (DataManager) : data manager
        """
        self.url = url
        parsed_url = urlparse(self.url)
        self.scheme = parsed_url.scheme if parsed_url.scheme else 'file'
        self.netloc = parsed_url.netloc
        self.path = parsed_url.path
        self.filename = os.path.basename(self.path)
        self.dman = dman if dman else DataManager.get_data_manager()
        self.data_future = {}
        if self.scheme != 'file':
            self.dman.add_file(self)

        self.cache = cache
        self.caching_dir = caching_dir
        self.staging = staging

    def __str__(self):
        return self.filepath

    def __repr__(self):
        return self.__str__()

    @property
    def filepath(self):
        """Return the resolved filepath on the side where it is called from.

        The appropriate filepath will be returned when called from within
        an app running remotely as well as regular python on the client side.

        Args:
            - self
        Returns:
             - filepath (string)
        """
        if self.scheme == 'globus':
            if hasattr(self, 'local_path'):
                return self.local_path

        if 'exec_site' not in globals() or self.staging == 'direct':
            # Assume local and direct
            return self.path
        else:
            # Return self.path for now
            return self.path

    def stage_in(self, site=None):
        """Transport file from the site of origin to local site."""
        return self.dman.stage_in(self, site)

    def stage_out(self):
        """Transport file from local filesystem to origin site."""
        return self.dman.stage_out(self)

    def set_data_future(self, df, site=None):
        self.data_future[site] = df

    def get_data_future(self, site):
        return self.data_future.get(site)


if __name__ == '__main__':

    x = File('./files.py')
