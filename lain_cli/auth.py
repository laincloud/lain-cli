# coding: utf-8

import re
import requests
from urllib import urlencode
from urlparse import urlparse, parse_qs

from lain_sdk.yaml.conf import user_config
import lain_sdk.mydocker as docker
from lain_sdk.util import error, warn

from lain_cli.utils import get_domain, save_config


SSO_URL_KEY = user_config.sso_url_key
SSO_TOKEN_KEY = user_config.sso_token_key
SSO_REFRESH_TOKEN_KEY = user_config.sso_refresh_token_key


class SSOAccess(object):
    """access to sso for SSOAccess"""

    client_id = ''
    client_secret = ''
    redirect_uri = ''
    grant_type = 'authorization_code'
    scope = 'write:group'
    auth_url = ''
    sso_url = ''
    authorization_endpoint = ''
    token_endpoint = ''
    userinfo_endpoint = ''

    def __init__(self, client_id, client_secret, redirect_uri, phase):
        SSOAccess.client_id = client_id
        SSOAccess.client_secret = client_secret
        SSOAccess.redirect_uri = redirect_uri
        SSOAccess.sso_url = self.get_sso_url(phase)
        SSOAccess.authorization_endpoint = SSOAccess.sso_url + '/oauth2/auth'
        SSOAccess.token_endpoint = SSOAccess.sso_url + '/oauth2/token'
        SSOAccess.userinfo_endpoint = SSOAccess.sso_url + '/api/me'
        SSOAccess.auth_url = SSOAccess.authorization_endpoint + '?' + urlencode({
            'client_id': client_id,
            'response_type': 'code',
            'scope': SSOAccess.scope,
            'redirect_uri': redirect_uri,
            'state': 'foobar',
        })

    @classmethod
    def new(cls, phase, cid=None, secret=None, redirect_uri=None):
        if cid is None:
            cid = 3
        if secret is None:
            secret = 'lain-cli_admin'
        if redirect_uri is None:
            redirect_uri = 'https://example.com'

        return SSOAccess(cid, secret, redirect_uri, phase)

    @classmethod
    def get_sso_url(cls, phase):
        try:
            sso_url = user_config.get_config().get(phase, {}).get(SSO_URL_KEY, None)
            if not sso_url:
                error(
                    'please set %s sso url by "lain config save %s %s ${%s_sso_url}"'
                    % (phase, phase, SSO_URL_KEY, phase))
                exit(1)
            return sso_url
        except Exception as e:
            error('error get %s sso url: %s' % (phase, e))
            return ''

    def get_auth_code(self, username, password):
        try:
            usr_msg = {'login': username, 'password': password}
            result = requests.post(
                self.auth_url,
                data=usr_msg,
                allow_redirects=False)
            code_callback_url = result.headers['Location']
            authentication = parse_qs(urlparse(code_callback_url).query)
            return True, authentication['code'][0]
        except Exception:
            warn("Please insure '%s' is accessable." % self.auth_url)
            warn("If not, please specify the sso cid and secret when login.")
            return False, ''

    def get_auth_token(self, code):
        try:
            auth_msg = {
                'client_id': self.client_id,
                'grant_type': 'authorization_code',
                'client_secret': self.client_secret,
                'code': code,
                'redirect_uri': self.redirect_uri
            }
            result = requests.request(
                "GET", self.token_endpoint,
                headers=None,
                params=auth_msg)
            accessinfo = result.json()
            return True, accessinfo['access_token'], accessinfo['refresh_token']
        except Exception:
            return False, '', ''

    def refresh_auth_token(self, refresh_token):
        try:
            auth_msg = {
                'client_id': self.client_id,
                'grant_type': 'refresh_token',
                'client_secret': self.client_secret,
                'refresh_token': refresh_token,
                'redirect_uri': self.redirect_uri
            }
            result = requests.request(
                "GET", self.token_endpoint,
                headers=None,
                params=auth_msg)
            # TODO http status code should be 200 if success
            # if refresh_token was expired, http status code should be 400
            accessinfo = result.json()
            assert accessinfo['access_token']
            assert accessinfo['refresh_token']
            return True, accessinfo['access_token'], accessinfo['refresh_token']
        except Exception:
            return False, '', ''

    @classmethod
    def save_token(cls, phase, access_token, refresh_token):
        try:
            save_config(phase, SSO_TOKEN_KEY, access_token)
            save_config(phase, SSO_REFRESH_TOKEN_KEY, refresh_token)
            return True
        except Exception as e:
            print(e)
            return False

    @classmethod
    def get_token(cls, phase):
        try:
            token = user_config.get_config().get(phase, {}).get(SSO_TOKEN_KEY, None)
            if not token:
                return 'unknown'
            return token
        except Exception:
            return 'unknown'

    @classmethod
    def get_refresh_token(cls, phase):
        try:
            token = user_config.get_config().get(phase, {}).get(SSO_REFRESH_TOKEN_KEY, None)
            if not token:
                return ''
            return token
        except Exception:
            return ''

    @classmethod
    def clear_token(cls, phase):
        return cls.save_token(phase, '', '')


def get_auth_header(access_token):
    return {'access-token': access_token}


def sso_login(phase, cid, secret, redirect_uri, username, password):
    sso_access = SSOAccess.new(phase, cid, secret, redirect_uri)
    get_code_success, code = sso_access.get_auth_code(username, password)
    if not get_code_success:
        warn('get_auth_code failed, username or password may be wrong.')
        return False
    get_token_success, access_token, refresh_token = sso_access.get_auth_token(code)
    if not get_token_success:
        warn('get_auth_token failed, sso client secret may be wrong.')
        return False
    save_token_success = sso_access.save_token(phase, access_token, refresh_token)
    if not save_token_success:
        warn('save_token failed')
        return False
    return True


def docker_login(phase, username, password):
    domain = get_domain(phase)
    return docker.login(username, password, 'registry.%s' % domain)


def sso_refresh(phase):
    sso_access = SSOAccess.new(phase, None, None, None)
    refresh_token = sso_access.get_refresh_token(phase)
    if not refresh_token:
        warn('refresh failed, no refresh token got')
        return False
    refresh_success, new_access_token, new_refresh_token = sso_access.refresh_auth_token(refresh_token)
    if not refresh_success:
        warn('refresh failed, refresh_auth_token failed ')
        return False
    save_token_success = sso_access.save_token(phase, new_access_token, new_refresh_token)
    if not save_token_success:
        warn('refresh failed, save_token failed')
        return False
    return True


def is_console_auth_activated(phase):
    domain = get_domain(phase)
    console = "console.%s" % domain
    apps_url = "http://%s/api/v1/apps/" % (console)

    apps_r = requests.get(apps_url)
    if apps_r.status_code == 401:
        return True
    elif apps_r.status_code == 200:
        return False
    else:
        error('shit happened when checking console auth status')
        error(apps_r.text)
        exit(1)


def get_role(phase, appname):
    # 404: {"msg": "user yisun4 does not exist in the app sso-ldap\n", "url": "/api/v1/repos/sso-ldap/maintainers/", "role": null}
    # 404: {"msg": "app with appname sso-ldap1 not exist", "url": "/api/v1/repos/", "role": null}
    # 401: {"msg": "unauthorized : don't have the access to the operation", "url": "/api/v1/docs/", "app": null}
    if not is_console_auth_activated(phase):
        return 'noauth-admin'
    no_role_pattern = re.compile(r"^user (.+) does not exist in the app (.+)$")
    no_app_pattern = re.compile(r"^app with appname (.+) not exist, has not been reposited yet")
    domain = get_domain(phase)
    console = "console.%s" % domain
    url = "http://%s/api/v1/repos/%s/roles/" % (console, appname)
    auth_header = get_auth_header(SSOAccess.get_token(phase))
    r = requests.get(url, headers=auth_header)
    if r.status_code == 401:
        return 'unauthorized'
    elif r.status_code == 200:
        try:
            r_json = r.json()
            return r_json["role"]["role"]
        except Exception as e:
            error(e)
            warn('DEBUG status: {}'.format(r.status_code))
            warn('DEBUG result: {}'.format(r.content))
            return 'error'
    elif r.status_code == 404:
        try:
            r_json = r.json()
            msg = r_json["msg"]
            if no_app_pattern.match(msg):
                return 'no app'
            elif no_role_pattern.match(msg):
                return 'no role'
            else:
                warn('DEBUG status: {}'.format(r.status_code))
                warn('unknown result: {}'.format(r_json))
                return 'unknown'
        except Exception as e:
            error(e)
            warn('DEBUG status: {}'.format(r.status_code))
            warn('DEBUG result: {}'.format(r.content))
            return 'error'
    else:
        warn('DEBUG status: {}'.format(r.status_code))
        warn('DEBUG content: {}'.format(r.content))
        return 'wrong status'


def authorize_and_check(phase, appname):
    role = get_role(phase, appname)

    # if unauthorized, refresh first
    if role == 'unauthorized':
        if not sso_refresh(phase):
            error('please login first')
            exit(1)
        role = get_role(phase, appname)
    # after refresh, should be authorized
    if role == 'unauthorized':
        error('still unauthorized after refresh')
        exit(1)
    elif role in ['wrong status', 'error', 'unknown']:
        error('shit happened when getting role')
        exit(1)
    elif role == 'no role':
        error('you have not a role of the app {}'.format(appname))
        error('please contact maintainers of the app')
        exit(1)
    elif role == 'no app':
        # no app, let it go
        warn('app {} does not exist, passed by.'.format(appname))
        return None
    else:
        # valid role
        return role
