#!/usr/bin/env python
# -*- coding: ISO-8859-1 -*-

##########################################################################################
#  @program        esgissue client                                                       #
#  @description    ESDOC ERRATA CLI                                                      #
#  @copyright      Copyright "(c)2016 Centre National de la Recherche Scientifique CNRS. #
#                             All Rights Reserved"                                       #
##########################################################################################

"""This module contains exception classes.

Note
    This module doesn't use any other (Synda) module and thus can be used
    everywhere (even in 'sdapp' module) without circular dependency problem.
"""


class GenericIssueClientException(Exception):
    def __init__(self, code=None, msg=None):
        self.code = code
        self.msg = msg

    def __str__(self):
        return "code={},message={}".format(self.code, self.msg)


class WSRequestFailedException(GenericIssueClientException):
    pass


class AuthenticationFailedException(GenericIssueClientException):
    pass


class AuthorizationFailedException(GenericIssueClientException):
    pass


class ServerIssueValidationFailedException(GenericIssueClientException):
    pass


class ServerDownException(GenericIssueClientException):
    pass
