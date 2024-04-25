import email
import json
import os
import smtplib
from email.header import decode_header
from email.message import Message
from email.mime.text import MIMEText

import boto3


def handler(event, context):
    try:
        return _handler(event, context)
    except:
        import traceback
        traceback.print_exc()
        return {}


def _handler(event, context):
    s3_client = boto3.client("s3")
    s3_bucket = os.getenv("S3_BUCKET")

    # メッセージIDとメールデータ取得
    message_id = event["Records"][0]["ses"]["mail"]["messageId"]
    s3_obj = s3_client.get_object(Bucket=s3_bucket, Key=message_id)
    raw_message = s3_obj["Body"].read()

    mail: Message = email.message_from_bytes(raw_message)
    # recipients = event['Records'][0]['ses']['receipt']['recipients']

    # Subject、From、body を取得
    subject = "\n".join(get_headers(mail, "subject"))
    mail_from = " ".join(get_headers(mail, "from"))
    body = mail.get_payload(decode=True).decode()

    # 転送する
    send_mail(
        os.getenv("EMAIL_FROM"),
        "somebody@example.com",
        f"【転送】{subject}",
        "\n".join(
            [
                f"from: {mail_from}",
                f"subject: {subject}",
                body,
            ]
        ),
    )
    return {}


def get_headers(mail: Message, header: str):
    return [
        (value.decode(encode or "ascii") if isinstance(value, bytes) else value)
        for value, encode in decode_header(mail.get(header))
    ]


def send_mail(mail_from, mail_to, subject, body):
    secret_id = os.getenv("SECRET_NAME")
    session = boto3.Session(region_name=os.getenv("AWS_REGION"))
    secret_value = session.client("secretsmanager").get_secret_value(SecretId=secret_id)
    secret = json.loads(secret_value["SecretString"])

    # メールを作る
    msg = MIMEText(body, "plain", "utf-8")
    msg["Subject"] = subject
    msg["From"] = mail_from
    msg["To"] = mail_to

    # SMTPサーバーに接続
    smtp = smtplib.SMTP(os.getenv("EMAIL_HOST"), int(os.getenv("EMAIL_PORT")))
    smtp.ehlo()
    try:
        smtp.starttls()
    except smtplib.SMTPNotSupportedError:
        pass
    smtp.login(secret["user"], secret["password"])

    # メール送信
    smtp.sendmail(mail_from, mail_to, msg.as_string())

    smtp.quit()
