from fastapi import Depends

from app.mail_sender import MailSender


class EmailService:
    def __init__(self, mail_sender: MailSender = Depends()):
        self.mail_sender = mail_sender

    def request_verify_token(self, email: str):


