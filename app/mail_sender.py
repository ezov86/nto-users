import smtplib

from app.config import Config


class MailSender:
    def __init__(self, config: Config = Depends(get_env)):
        self.env = env
        self.server = smtplib.SMTP(host=self.env.SMTP_HOST, port=self.env.SMTP_PORT)
        # self.server.login(self.env.SMTP_USER, self.env.SMTP_PASSWORD)

    def send_verification_mail(self, email: str, token: str):
        msg = MIMEMultipart()
        msg["From"] = self.env.SMTP_FROM
        msg["To"] = email
        msg["Subject"] = "Account verification"

        link = self.env.VERIFY_URL + "/" + token

        message = f'<a href="{link}">Verify your account</a>'
        msg.attach(MIMEText(message, "html"))

        self.server.sendmail(self.env.SMTP_FROM, email, msg.as_string())

    def send_password_update_mail(self, email: str, token: str):
        msg = MIMEMultipart()
        msg["From"] = self.env.SMTP_FROM
        msg["To"] = email
        msg["Subject"] = "Password changing"

        link = self.env.PWD_UPDATE_URL + "/" + token

        message = f'<a href="{link}">Change your password</a>'
        msg.attach(MIMEText(message, "html"))

        self.server.sendmail(self.env.SMTP_FROM, email, msg.as_string())