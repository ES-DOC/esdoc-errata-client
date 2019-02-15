#!/usr/bin/env python
"""
   :platform: Unix
   :synopsis: Errata object factory.

"""
from constants import VISUAL_SEPARATOR
errata_viewer_url_base = 'https://errata.es-doc.org/static/view.html?uid='


class ErrataObject(object):
    """
    This object represents the errata API return when querying the pid or simple-pid endpoints
    You'll notice subcommand is passed to the object, this is used to cover both simple and complex PID responses
    which are different.
    """

    def __init__(self, response):
        self.has_errata = response[0] is not None
        self.errata_ids = response[0]
        self.version = response[2]
        self.drs = response[1]
        self.is_latest = False
        self.is_queried = False
        self.is_first = False
        self._check_for_multiple_errata()

    def __str__(self):
        result_string = ''
        if self.has_errata:
            for errata_id in self.errata_ids_list:
                result_string+= (self.drs + '#' + self.version).center(10, '-') + VISUAL_SEPARATOR + (
                    'QUERIED'.center(10, '-') if self.is_queried else 'LATEST'.center(10, '-') if self.is_latest
                    else 'FIRST'.center(10, '-') if self.is_first else ''.center(10, '-')) + VISUAL_SEPARATOR + (
                           errata_viewer_url_base + str(errata_id) if
                           self.has_errata else ''.center(10, '-'))
                if self.errata_ids_list > 1:
                    result_string+='\n'
        return result_string

    def _check_for_multiple_errata(self):
        # Checks for the case where multiple errata ids are found for a single dataset/file
        # instead of double ErrataObjects, it's taken care of in printing.
        self.errata_ids_list = self.errata_ids.split(';')



class ErrataCollectionObject(object):
    """
    This object is dedicated to wrapping a series of errata objects.
    """

    def __init__(self):
        self.listOfErrataObjects = []
        self.drs = None
    def __str__(self):
        result_string = ''
        for errataElement in self.listOfErrataObjects:
            result_string+=str(errataElement)
        if len(self.listOfErrataObjects) > 1:
            result_string+='\n'
        return result_string

    def append_errata_object(self, errata_object):
        self.listOfErrataObjects.append(errata_object)
        if self.drs is None:
            self.drs=errata_object.drs