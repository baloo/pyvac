# Import smtplib for the actual sending function
import smtplib
# Import the email modules we'll need
import email
import email.charset
from email.mime.text import MIMEText
from email.utils import formatdate
import logging

log = logging.getLogger(__name__)

# Init email module properties, we prefer quoted-printable encoded fields
email.charset.add_charset('utf-8', email.charset.QP, email.charset.QP, 'utf-8')


class SmtpWrapper(object):
    """ Simple smtp class wrapper"""
    host = None
    port = None
    starttls = None
    must_auth = None
    starttls = None
    login = None
    password = None
    _from = None

    def __init__(self, config):

        self.signature = config['signature']
        self.host = config['host']
        self.port = config.get('port', 25)
        self.starttls = config['starttls']
        self.must_auth = config['must_auth']
        self.login = config['login']
        self.password = config['password']
        self._from = config['from']

        log.info('Smtp wrapper initialized')

    def send_mail(self, sender, target, subject, content, tracking_id=None):
        """ Send a mail through smtp using given parameters """

        content = """%s

%s
""" % (content, self.signature)

        msg = MIMEText(content.encode('utf-8'), 'plain', 'utf-8')

        msg['Subject'] = '[Pyvac] %s' % subject
        msg['From'] = sender
        msg['To'] = target
        msg['Date'] = formatdate()

        conn = smtplib.SMTP(self.host, self.port)
        if self.starttls:
            conn.starttls()
        _from = self._from if self._from else sender
        conn.sendmail(_from, [target], msg.as_string())
        conn.quit()

        log.info('Message sent through SMTP: (%s) %s -> %s [%s]' %
                 (subject, sender, target, tracking_id or ''))


class SmtpCache(object):
    """ Email cache class singleton """
    _instance = None

    def __new__(cls, *args, **kwargs):
        if not cls._instance:
            raise RuntimeError('Email is not initialized')

        return cls._instance

    @classmethod
    def configure(cls, settings):
        cls._instance = cls.from_config(settings)

    @classmethod
    def from_config(cls, config, **kwargs):
        """
        Return a Email object configured from the given configuration.
        """
        return SmtpWrapper(config)
