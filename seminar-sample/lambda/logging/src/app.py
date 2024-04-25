import json
import os
import random
import string
from datetime import datetime
from functools import cached_property

import boto3
import psycopg2

# FIXME:log_session や action_log のようなテーブルがあることを想定したログ保存Lambda（サンプルのため未稼働）


def handler(event, context):
    try:
        return _handler(event, context)
    except:
        import traceback

        traceback.print_exc()
        return dict(
            statusCode=500,
            body=json.dumps(dict(result="error")),
        )


def _handler(event, context):
    executor = RequestExecutor(context)
    if "Records" in event:
        for ev in event["Records"]:
            executor.handle(ev.get("body"), ev.get("attributes", {}).get("SentTimestamp"))
    elif "requestContext" in event:
        executor.handle(event, event.get("requestContext", {}).get("requestTimeEpoch"))
    else:
        print(event)
    return executor.finalize()


class RequestExecutor:
    def __init__(self, context):
        self.context = context
        self.region = os.getenv("AWS_REGION")
        self.endpoint_url = os.getenv("AWS_ENDPOINT_URL")
        self.session = boto3.Session(region_name=self.region)
        self.log_records: list[dict] = []

    @cached_property
    def secrets_manager(self):
        return self.session.client(service_name="secretsmanager", endpoint_url=self.endpoint_url)

    @cached_property
    def connection(self):
        secret_id = os.getenv("SECRET_NAME")
        secret_value = self.secrets_manager.get_secret_value(SecretId=secret_id)
        db_secret = json.loads(secret_value["SecretString"])
        params = dict(
            host=os.getenv("DATABASE_HOST"),
            port=5432,
            dbname=os.getenv("DATABASE_NAME"),
            user=db_secret["username"],
            password=db_secret["password"],
        )
        dsn = " ".join(f"{name}={value}" for name, value in params.items() if value)
        # print(dsn)
        return psycopg2.connect(dsn=dsn)

    @cached_property
    def cursor(self):
        return self.connection.cursor()

    def _execute(self, query, vars=None):
        # print(query, vars)
        return self.cursor.execute(query, vars)

    def handle(self, event, timestamp=None):
        if isinstance(event, str):
            event = json.loads(event)
        request_time = datetime.fromtimestamp(float(timestamp) / 1000) if timestamp else datetime.now()

        headers = event.get("headers", {})
        body = event.get("body")
        if isinstance(body, str):
            try:
                body = json.loads(event.get("body"))
            except json.JSONDecodeError:
                body = {}

        session_key, session_id = self.get_session(headers, body, request_time)

        data = body.get("data")
        self.log_records.append(
            dict(
                timestamp=request_time.isoformat(),
                session_id=session_id,
                data=json.dumps(data) if data else None,
                session_key=session_key,
            )
        )

    def get_session(self, headers: dict, body: dict, request_time: datetime) -> tuple[str, int]:
        for key, value in headers.items():  # type:str,str
            if key.lower() == "x-session":  # X-Session がどこかで x-session になるぽい?
                session_key = value
                break
        else:
            session_key = None

        session_id = self.get_session_id(session_key) if session_key else None
        if not session_id:
            session_key = self.generate_session_key()
            session_id = self.create_session_key(request_time, session_key, headers, body.get("parameters"))
        return session_key, session_id

    def create_session_key(self, timestamp: datetime, session_key, headers=None, parameters=None):
        if headers is not None:
            headers = json.dumps(headers)
        if parameters is not None:
            parameters = json.dumps(parameters)
        self._execute(
            "INSERT INTO log_session (created_at,session_key,headers,parameters) VALUES (%s,%s,%s,%s) RETURNING id;",
            (timestamp.isoformat(), session_key, headers, parameters),
        )
        row = self.cursor.fetchone()
        return row[0] if row else None

    def generate_session_key(self, length=20, retry=5) -> str:
        letters = string.ascii_letters + string.digits
        for _ in range(retry):
            session_key = "".join(random.choice(letters) for _ in range(length))
            if not self.get_session_id(session_key):
                return session_key
        raise Exception()

    def get_session_id(self, session_key):
        self._execute(
            "SELECT id FROM log_session WHERE session_key=%s;",
            (session_key,),
        )
        row = self.cursor.fetchone()
        return row[0] if row else None

    def finalize(self):
        if self.log_records:
            self._execute(
                "INSERT INTO action_log (timestamp,session_id,data) VALUES {};".format(
                    ",".join(["(%s,%s,%s,%s)"] * len(self.log_records))
                ),
                sum(
                    [
                        [record.get(field) for field in "timestamp,session_id,data".split(",")]
                        for record in self.log_records
                    ],
                    start=[],
                ),
            )
            self.connection.commit()
            return dict(
                statusCode=200,
                body=json.dumps(
                    {
                        "data": {
                            "type": "logging",
                            "attributes": {"session_key": self.log_records[-1].get("session_key")},
                        }
                    }
                ),
            )
        else:
            return dict(statusCode=403)
