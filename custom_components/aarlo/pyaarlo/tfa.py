import email
import imaplib
import re
import time

import requests


class Arlo2FAConsole:
    """ 2FA authentication via console.
    Accepts input from console and returns that for 2FA.
    """

    def __init__(self, arlo):
        self._arlo = arlo

    def start(self):
        self._arlo.debug('2fa-console: starting')
        return True

    def get(self):
        self._arlo.debug('2fa-console: checking')
        return input('Enter Code: ')

    def stop(self):
        self._arlo.debug('2fa-console: stopping')


class Arlo2FAImap:
    """ 2FA authentication via IMAP
    Connects to IMAP server and waits for email from Arlo with 2FA code in it.

    Note: will probably need tweaking for other IMAP setups...
    """

    def __init__(self, arlo):
        self._arlo = arlo
        self._imap = None
        self._old_ids = None
        self._new_ids = None

    def start(self):
        self._arlo.debug('2fa-imap: starting')

        # clean up
        if self._imap is not None:
            self.stop()

        self._imap = imaplib.IMAP4_SSL(self._arlo.cfg.tfa_host)
        res, status = self._imap.login(self._arlo.cfg.tfa_username, self._arlo.cfg.tfa_password)
        if res.lower() != 'ok':
            self._arlo.debug('imap login failed')
            return False
        res, status = self._imap.select()
        if res.lower() != 'ok':
            self._arlo.debug('imap select failed')
            return False
        res, self._old_ids = self._imap.search(None, 'FROM', 'do_not_reply@arlo.com')
        if res.lower() != 'ok':
            self._arlo.debug('imap search failed')
            return False

        self._new_ids = self._old_ids
        self._arlo.debug("old-ids={}".format(self._old_ids))
        if res.lower() == 'ok':
            return True

        return False

    def get(self):
        self._arlo.debug('2fa-imap: checking')

        # give tfa_total_timeout seconds for email to arrive
        start = time.time()
        while True:

            # wait a short while, stop after a total timeout
            # ok to do on first run gives email time to arrive
            time.sleep(self._arlo.cfg.tfa_timeout)
            if time.time() > (start + self._arlo.cfg.tfa_total_timeout):
                return None

            # grab new email ids
            self._imap.check()
            res, self._new_ids = self._imap.search(None, 'FROM', 'do_not_reply@arlo.com')
            self._arlo.debug("2fa-imap: new-ids={}".format(self._new_ids))
            if self._new_ids == self._old_ids:
                self._arlo.debug("2fa-imap: no change in emails")
                continue

            # new message...
            old_ids = self._old_ids[0].split()
            for msg_id in self._new_ids[0].split():

                # seen it?
                if msg_id in old_ids:
                    continue

                # new message. look for HTML part and look code code in it
                self._arlo.debug("2fa-imap: new-msg={}".format(msg_id))
                res, msg = self._imap.fetch(msg_id, '(RFC822)')
                for part in email.message_from_bytes(msg[0][1]).walk():
                    if part.get_content_type() == 'text/html':
                        for line in part.get_payload().splitlines():

                            # match code in email, this might need some work if the email changes
                            code = re.match(r'^\W*(\d{6})\W*$', line)
                            if code is not None:
                                self._arlo.debug("2fa-imap: code={}".format(code.group(1)))
                                return code.group(1)

            # update old so we don't keep trying new
            self._old_ids = self._new_ids

        return None

    def stop(self):
        self._arlo.debug('2fa-imap: stopping')

        self._imap.close()
        self._imap.logout()
        self._imap = None
        self._old_ids = None
        self._new_ids = None


class Arlo2FARestAPI:
    """ 2FA authentication via rest API.
    Queries web site until code appears
    """

    def __init__(self, arlo):
        self._arlo = arlo

    def start(self):
        self._arlo.debug('2fa-rest-api: starting')
        if self._arlo.cfg.tfa_host is None or self._arlo.cfg.tfa_password is None:
            self._arlo.debug('2fa-rest-api: invalid config')
            return False

        self._arlo.debug("2fa-rest-api: clearing")
        response = requests.get(
            "{}/clear?email={}&token={}".format(self._arlo.cfg.tfa_host, self._arlo.cfg.tfa_username,
                                                self._arlo.cfg.tfa_password), timeout=10)
        if response.status_code != 200:
            self._arlo.debug("2fa-rest-api: possible problem clearing")

        return True

    def get(self):
        self._arlo.debug('2fa-rest-api: checking')

        # give tfa_total_timeout seconds for email to arrive
        start = time.time()
        while True:

            # wait a short while, stop after a total timeout
            # ok to do on first run gives email time to arrive
            time.sleep(self._arlo.cfg.tfa_timeout)
            if time.time() > (start + self._arlo.cfg.tfa_total_timeout):
                return None

            # Try for the token.
            self._arlo.debug("2fa-rest-api: checking")
            response = requests.get(
                "{}/get?email={}&token={}".format(self._arlo.cfg.tfa_host, self._arlo.cfg.tfa_username,
                                                  self._arlo.cfg.tfa_password), timeout=10
            )
            if response.status_code == 200:
                code = response.json().get('data', {}).get('code', None)
                if code is not None:
                    self._arlo.debug("2fa-rest-api: code={}".format(code))
                    return code

            self._arlo.debug('2fa-rest-api: retrying')

    def stop(self):
        self._arlo.debug('2fa-rest-api: stopping')
