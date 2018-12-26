#!/usr/bin/env python
"""
   :platform: Unix
   :synopsis: Errata object factory.

"""


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

    def __repr__(self):
        if self.has_errata:
            return 'DRS: ' + self.drs + '\n' + 'version: ' + self.version + '\n' + 'has errata: ' + str(self.has_errata)\
                   + '\n' + 'errata ids: ' + str(self.errata_ids) + '\n' + 'latest: ' + str(self.is_latest)
        else:
            return 'DRS: ' + self.drs + '\n' + 'version: ' + self.version+ '\n'+ 'has errata: '+str(self.has_errata) + \
                   '\n' + 'latest: ' + str(self.is_latest)


class ErrataCollectionObject(object):
    """
    This object is dedicated to wrapping a series of errata objects.
    """
    def __init__(self):
        self.listOfErrataObjects = []

    # def __str__(self):
    #     print("Errata objects found: %d" % len(self.listOfErrataObjects))
    #     print(self.listOfErrataObjects)
    #     for element in self.listOfErrataObjects:
    #         print(element)
    def __repr__(self):
        print("Errata objects found: %d" % len(self.listOfErrataObjects))
        return str(self.listOfErrataObjects)

    def append_errata_object(self, errataObject):
        self.listOfErrataObjects.append(errataObject)
