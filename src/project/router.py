from django.conf import settings
from django.db import models


class ReplicaRouter:
    REPLICA_NAME = "replica"

    def db_for_read(self, model: models.Model, **hints):
        # read はリードレプリカの設定があればそれを用いる
        if self.has_replica:
            return self.REPLICA_NAME

    def db_for_write(self, model: models.Model, **hints):
        # 'default' を期待して次の Router に委ねる
        return None

    def allow_relation(self, obj1, obj2, **hints):
        return True

    def allow_migrate(self, db, app_label, model_name=None, **hints):
        # None を返して次の Router に委ねる
        return None

    @property
    def has_replica(self):
        return self.REPLICA_NAME in settings.DATABASES


class DefaultRouter:
    DEFAULT_NAME = "default"

    def db_for_read(self, model: models.Model, **hints):
        return self.DEFAULT_NAME

    def db_for_write(self, model: models.Model, **hints):
        return self.DEFAULT_NAME

    def allow_relation(self, obj1, obj2, **hints):
        return True

    def allow_migrate(self, db, app_label, model_name=None, **hints):
        return True
