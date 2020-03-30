import email
import imaplib
import re
import time

from .constant import (
    TFA_CONSOLE_SOURCE,
    TFA_IMAP_SOURCE)


class Arlo2FA:

    def __init__(self, arlo):
        self._arlo = arlo
        self._imap = None
        self._old_ids = None
        self._new_ids = None

    def start(self):
        self._arlo.debug('2fa is using {}'.format(self._arlo.cfg.tfa_source))

        # console, always works!
        if self._arlo.cfg.tfa_source == TFA_CONSOLE_SOURCE:
            return True

        # imap, grab snapshot of current IDs
        elif self._arlo.cfg.tfa_source == TFA_IMAP_SOURCE:
            self._imap = imaplib.IMAP4_SSL(self._arlo.cfg.imap_host)
            res, status = self._imap.login(self._arlo.cfg.imap_username, self._arlo.cfg.imap_password)
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
        self._arlo.debug('2fa checking')

        # console, wait until the user finishes
        if self._arlo.cfg.tfa_source == TFA_CONSOLE_SOURCE:
            return input('Enter Code: ')

        # give tfa_total_timeout seconds for email to arrive
        elif self._arlo.cfg.tfa_source == TFA_IMAP_SOURCE:

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
                self._arlo.debug("new-ids={}".format(self._new_ids))
                if self._new_ids == self._old_ids:
                    self._arlo.debug("no change in emails")
                    continue

                # new message...
                old_ids = self._old_ids[0].split()
                for msg_id in self._new_ids[0].split():

                    # seen it?
                    if msg_id in old_ids:
                        continue

                    # new message. look for HTML part and look code code in it
                    self._arlo.debug("new-msg={}".format(msg_id))
                    res, msg = self._imap.fetch(msg_id, '(RFC822)')
                    for part in email.message_from_bytes(msg[0][1]).walk():
                        if part.get_content_type() == 'text/html':
                            for line in part.get_payload().splitlines():

                                # match code in email, this might need some work if the email changes
                                code = re.match(r'^\W*(\d{6})\W*$', line)
                                if code is not None:
                                    self._arlo.debug("code={}".format(code.group(1)))
                                    return code.group(1)

                # update old so we don't keep trying new
                self._old_ids = self._new_ids

        return None

    def stop(self):

        if self._arlo.cfg.tfa_source == TFA_IMAP_SOURCE:
            self._imap.close()
            self._imap.logout()
