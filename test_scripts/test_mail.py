from multiprocessing import Process
from email.header import Header
from email.mime.text import MIMEText
import smtplib


class MailSender(object):
    def __init__(self):
        self.mail_server = 'smtp.qq.com'
        self.mail_ssl_port = 465
        self.mail_form_user = '996846239@qq.com'
        self.mail_passwd = 'qxhonddalbdtbaja'

    def _send(self, title, content, to_address):
        msg = MIMEText(content)
        msg['From'] = self.mail_form_user
        msg['To'] = ','.join(to_address)
        msg['Subject'] = Header(title, "utf-8").encode()
        server = smtplib.SMTP_SSL(self.mail_server, self.mail_ssl_port)
        server.login(self.mail_form_user, self.mail_passwd)
        server.sendmail(self.mail_form_user, to_address, msg.as_string())
        server.quit()

    def send_email(self, title, content, to_address):
        p = Process(target=self._send, args=(title, content, to_address))
        p.start()

if __name__ == '__main__':
    m = MailSender()
    m.send_email('顶村顶', 'x压顶村顶戴模压英雄无用武之地地xx', ['2510233678@qq.com'])