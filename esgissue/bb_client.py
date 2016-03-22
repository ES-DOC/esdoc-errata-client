#!/usr/bin/env python
"""
   :platform: Unix
   :synopsis: Lite BitBucket client for ESGF Issue Manager based on bitbucket-api 0.5.0

"""

import json
import logging
import re
from urlparse import parse_qs
from requests import Request, Session, post
from requests_oauthlib import OAuth1


URLS = {
    'BASE': 'https://api.bitbucket.org/%s/%s',
    'GET_USER': 'users/%(username)s/',
    'REQUEST_TOKEN': 'oauth/request_token/',
    'AUTHENTICATE': 'oauth/authenticate?oauth_token=%(token)s',
    'ACCESS_TOKEN': 'oauth/access_token/',
    'CREATE_REPO': 'repositories/',
    'GET_REPO': 'repositories/%(username)s/%(repo)s/',
    'UPDATE_REPO': 'repositories/%(username)s/%(repo)s/',
    'DELETE_REPO': 'repositories/%(username)s/%(repo)s/',
    'GET_ARCHIVE': 'repositories/%(username)s/%(repo)s/%(format)s/master/',
    'GET_ISSUES': 'repositories/%(username)s/%(repo)s/issues/',
    'GET_ISSUE': 'repositories/%(username)s/%(repo)s/issues/%(issue_id)s/',
    'CREATE_ISSUE': 'repositories/%(username)s/%(repo)s/issues/',
    'UPDATE_ISSUE': 'repositories/%(username)s/%(repo)s/issues/%(issue_id)s/',
    'DELETE_ISSUE': 'repositories/%(username)s/%(repo)s/issues/%(issue_id)s/'
}


class Bitbucket(object):
    """
    This class lets you interact with the BitBucket public API.

    """
    def __init__(self, username='', password='', team='', repo=''):
        self.username = username
        self.password = password
        self.team = team
        self.repo = repo

        self.repository = Repository(self)
        self.issue = Issue(self)

        self.access_token = None
        self.access_token_secret = None
        self.consumer_key = None
        self.consumer_secret = None
        self.oauth = None

    @property
    def auth(self):
        """
        Returns credentials for current BitBucket user.

        """
        if self.oauth:
            return self.oauth
        return (self.username, self.password)

    @property
    def username(self):
        """
        Returns repository's username.

        """
        return self._username

    @username.setter
    def username(self, value):
        try:
            if isinstance(value, basestring):
                self._username = unicode(value)
        except NameError:
            self._username = value

        if value is None:
            self._username = None

    @username.deleter
    def username(self):
        del self._username

    @property
    def password(self):
        """
        Returns repository's password.

        """
        return self._password

    @password.setter
    def password(self, value):
        try:
            if isinstance(value, basestring):
                self._password = unicode(value)
        except NameError:
            self._password = value

        if value is None:
            self._password = None

    @password.deleter
    def password(self):
        del self._password

    @property
    def repo(self):
        """
        Returns repository's name.

        """
        return self._repo

    @repo.setter
    def repo(self, value):
        if value is None:
            self._repo = None
        else:
            try:
                if isinstance(value, basestring):
                    value = unicode(value)
            except NameError:
                pass
            value = value.lower()
            self._repo = re.sub(r'[^a-z0-9_-]+', '-', value)

    @repo.deleter
    def repo(self):
        del self._repo

    @property
    def team(self):
        """
        Returns team's name.

        """
        return self._team

    @team.setter
    def team(self, value):
        try:
            if isinstance(value, basestring):
                self._team = unicode(value)
        except NameError:
            self._team = value

        if value is None:
            self._team = None

    @team.deleter
    def team(self):
        del self._team

    def authorize(self, consumer_key, consumer_secret, callback_url=None, access_token=None, access_token_secret=None):
        """
        Call this with your consumer key, secret and callback URL, to generate a token for verification.

        """
        self.consumer_key = consumer_key
        self.consumer_secret = consumer_secret

        if not access_token and not access_token_secret:
            if not callback_url:
                return False, "Callback URL is missing"
            oauth = OAuth1(
                consumer_key,
                client_secret=consumer_secret,
                callback_uri=callback_url)
            r = requests.post(self.url('REQUEST_TOKEN'), auth=oauth)
            if r.status_code == 200:
                creds = parse_qs(r.content)

                self.access_token = creds.get('oauth_token')[0]
                self.access_token_secret = creds.get('oauth_token_secret')[0]
            else:
                return (False, r.content)
        else:
            self.finalize_oauth(access_token, access_token_secret)

        return (True, None)

    def verify(self, verifier, consumer_key=None, consumer_secret=None, access_token=None, access_token_secret=None):
        """
        After converting the token into verifier, call this to finalize the
        authorization.
        
        """
        self.consumer_key = consumer_key or self.consumer_key
        self.consumer_secret = consumer_secret or self.consumer_secret
        self.access_token = access_token or self.access_token
        self.access_token_secret = access_token_secret or self.access_token_secret

        oauth = OAuth1(
            self.consumer_key,
            client_secret=self.consumer_secret,
            resource_owner_key=self.access_token,
            resource_owner_secret=self.access_token_secret,
            verifier=verifier)
        r = post(self.url('ACCESS_TOKEN'), auth=oauth)
        if r.status_code == 200:
            creds = parse_qs(r.content)
        else:
            return False, r.content

        self.finalize_oauth(creds.get('oauth_token')[0],
                            creds.get('oauth_token_secret')[0])
        return True, None

    def finalize_oauth(self, access_token, access_token_secret):
        """
        Called internally once auth process is complete.
        """
        self.access_token = access_token
        self.access_token_secret = access_token_secret

        # Final OAuth object
        self.oauth = OAuth1(
            self.consumer_key,
            client_secret=self.consumer_secret,
            resource_owner_key=self.access_token,
            resource_owner_secret=self.access_token_secret)

    @staticmethod
    def dispatch(method, url, auth=None, params=None, **kwargs):
        """
        Send HTTP request, with given method, credentials and data to the given URL, and return the success and the
        result on success.

        """
        r = Request(method=method,
                    url=url,
                    auth=auth,
                    params=params,
                    data=kwargs)
        s = Session()
        resp = s.send(r.prepare())
        status = resp.status_code
        text = resp.text
        error = resp.reason
        if 200 <= status < 300:
            if text:
                try:
                    return True, json.loads(text)
                except TypeError:
                    pass
                except ValueError:
                    pass
            return True, text
        elif 300 <= status < 400:
            return False, 'Unauthorized access, please check your credentials.'
        elif 400 <= status < 500:
            return False, 'Service not found.'
        elif 500 <= status < 600:
            return False, 'Server error.'
        else:
            return False, error

    @staticmethod
    def url(action, api_version='2.0', **kwargs):
        """
        Construct and return the URL for a specific API service.

        """
        url = URLS['BASE'] % (api_version, URLS[action]) % kwargs
        logging.debug('{0} on {1}'.format(action, url))
        return url

    def get_user(self, username=None):
        """
        Returns user information. If username is not defined, tries to return own information.

        """
        username = username or self.username or ''
        url = self.url('GET_USER', api_version='2.0', username=username)
        return self.dispatch('GET', url)


class Issue(object):
    """
    This class provide issue-related methods to BitBucket objects.

    """

    def __init__(self, bitbucket, issue_id=None):
        self.bitbucket = bitbucket
        self.issue_id = issue_id

    @property
    def issue_id(self):
        """
        Returns issue id.

        """
        return self._issue_id

    @issue_id.setter
    def issue_id(self, value):
        if value:
            self._issue_id = int(value)
        elif value is None:
            self._issue_id = None

    @issue_id.deleter
    def issue_id(self):
        del self._issue_id

    def all(self, username=None, repo=None, params=None):
        """
        Get issues from one of the team's repositories. If team is not defined, tries to get issues from one of the
        user's repositories.

        """
        username = self.bitbucket.team or username or self.bitbucket.username or ''
        repo = repo or self.bitbucket.repo or ''
        url = self.bitbucket.url('GET_ISSUES', api_version='2.0', username=username, repo=repo)
        return self.bitbucket.dispatch('GET', url, auth=self.bitbucket.auth, params=params)

    def get(self, issue_id, username=None, repo=None):
        """
        Get an issue from one of the user's or team's repositories.

        """
        username = self.bitbucket.team or username or self.bitbucket.username or ''
        repo = repo or self.bitbucket.repo or ''
        url = self.bitbucket.url('GET_ISSUE', api_version='2.0', username=username, repo=repo, issue_id=issue_id)
        return self.bitbucket.dispatch('GET', url, auth=self.bitbucket.auth)

    def create(self, username=None, repo=None, **kwargs):
        """
        Add an issue to one of user's or team's repositories.
        Each issue require a different set of attributes,
        you can pass them as keyword arguments (attributename='attributevalue').
        Attributes are:

            * title: The title of the new issue.
            * content: The content of the new issue.
            * component: The component associated with the issue.
            * milestone: The milestone associated with the issue.
            * version: The version associated with the issue.
            * responsible: The username of the person responsible for the issue.
            * status: The status of the issue (new, open, resolved, on hold, invalid, duplicate, or wontfix).
            * kind: The kind of issue (bug, enhancement, or proposal).
        """
        username = self.bitbucket.team or username or self.bitbucket.username or ''
        repo = repo or self.bitbucket.repo or ''
        url = self.bitbucket.url('CREATE_ISSUE', api_version='1.0', username=username, repo=repo)
        return self.bitbucket.dispatch('POST', url, auth=self.bitbucket.auth, **kwargs)

    def update(self, issue_id, username=None, repo=None, **kwargs):
        """
        Update an issue to one of user's or team's repositories.
        Each issue require a different set of attributes,
        you can pass them as keyword arguments (attributename='attributevalue').
        Attributes are:

            * title: The title of the new issue.
            * content: The content of the new issue.
            * component: The component associated with the issue.
            * milestone: The milestone associated with the issue.
            * version: The version associated with the issue.
            * responsible: The username of the person responsible for the issue.
            * status: The status of the issue (new, open, resolved, on hold, invalid, duplicate, or wontfix).
            * kind: The kind of issue (bug, enhancement, or proposal).
        """
        username = self.bitbucket.team or username or self.bitbucket.username or ''
        repo = repo or self.bitbucket.repo or ''
        url = self.bitbucket.url('UPDATE_ISSUE', api_version='1.0', username=username, repo=repo, issue_id=issue_id)
        return self.bitbucket.dispatch('PUT', url, auth=self.bitbucket.auth, **kwargs)

    def delete(self, issue_id, username=None, repo=None):
        """
        Delete an issue from one of user's or team's repositories.

        """
        username = self.bitbucket.team or username or self.bitbucket.username or ''
        repo = repo or self.bitbucket.repo or ''
        url = self.bitbucket.url('DELETE_ISSUE', api_version='2.0', username=username, repo=repo, issue_id=issue_id)
        return self.bitbucket.dispatch('DELETE', url, auth=self.bitbucket.auth)


class Repository(object):
    """
    This class provide repository-related methods to BitBucket objects.

    """

    def __init__(self, bitbucket):
        self.bitbucket = bitbucket

    def public(self, username=None):
        """
        Returns all public repositories from an user or a team. If username is not defined, tries to return own public
        repository.

        """
        username = self.bitbucket.team or username or self.bitbucket.username or ''
        url = self.bitbucket.url('GET_USER', api_version='2.0', username=username)
        response = self.bitbucket.dispatch('GET', url)
        try:
            return response[0], response[1]['repositories']
        except TypeError:
            pass
        return response

    def all(self, username=None):
        """
        Return all repositories from an user or a team. If username is not defined, tries to return own repositories.

        """
        username = self.bitbucket.team or username or self.bitbucket.username or ''
        url = self.bitbucket.url('GET_USER', api_version='2.0', username=username)
        response = self.bitbucket.dispatch('GET', url, auth=self.bitbucket.auth)
        try:
            return response[0], response[1]['repositories']
        except TypeError:
            pass
        return response

    def get(self, username=None, repo=None):
        """
        Get a single repository from an user of a team and return it.

        """
        username = self.bitbucket.team or username or self.bitbucket.username or ''
        repo = repo or self.bitbucket.repo or ''
        url = self.bitbucket.url('GET_REPO', api_version='2.0', username=username, repo=repo)
        return self.bitbucket.dispatch('GET', url, auth=self.bitbucket.auth)

    def create(self, repo_name, scm='git', private=True, **kwargs):
        """
        Creates a new repository fro a user of a team on Bitbucket and return it.

        """
        url = self.bitbucket.url('CREATE_REPO', api_version='2.0')
        return self.bitbucket.dispatch('POST', url, auth=self.bitbucket.auth,
                                                    name=repo_name,
                                                    scm=scm,
                                                    is_private=private, **kwargs)

    def update(self, username=None, repo=None, **kwargs):
        """
        Updates repository from a user or a team and return it.

        """
        username = self.bitbucket.team or username or self.bitbucket.username or ''
        repo = repo or self.bitbucket.repo or ''
        url = self.bitbucket.url('UPDATE_REPO', api_version='2.0', username=username, repo=repo)
        return self.bitbucket.dispatch('PUT', url, auth=self.bitbucket.auth, **kwargs)

    def delete(self, username=None, repo=None):
        """
        Delete a repository from a user of a team. Please use with caution as there is NO confirmation and NO undo.

        """
        username = self.bitbucket.team or username or self.bitbucket.username or ''
        repo = repo or self.bitbucket.repo or ''
        url = self.bitbucket.url('DELETE_REPO', api_version='2.0', username=username, repo=repo)
        return self.bitbucket.dispatch('DELETE', url, auth=self.bitbucket.auth)