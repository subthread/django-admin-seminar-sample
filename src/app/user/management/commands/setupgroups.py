from django.conf import settings
from django.contrib.auth.models import Group, Permission
from django.core.management import BaseCommand
from django.db import transaction


class Command(BaseCommand):
    help = "グループをを用意する"

    setup_groups = {
        settings.ALL_USER_GROUP_NAME: [
            # ユーザー情報確認／自分のユーザー情報は編集可能にする
            "view_serviceuser",
            #
            # app.activity 活動記録
            "view_activitysummary",
            "add_activitysummary",
            "change_activitysummary",
            "delete_activitysummary",
            # app.activity ダウンロード
            "view_activityarchive",
            #
            # app.readlog 読書ログの表示／追加／変更／削除
            "view_readlog",
            "add_readlog",
            "change_readlog",
            "delete_readlog",
            # app.readlog 書誌情報の表示／追加／変更
            "view_bibliographic",
            "add_bibliographic",
            "change_bibliographic",
            # app.readlog 著者情報の表示／追加／変更
            "view_author",
            "add_author",
            "change_author",
            # app.readlog 出版社情報の表示／追加／変更
            "view_publisher",
            "add_publisher",
            "change_publisher",
            # app.readlog インポート
            "add_importbibliographic",
            "change_importbibliographic",
            "view_importbibliographic",
        ],
        settings.GOOGLE_USER_GROUP_NAME: [],
    }

    def handle(self, *args, **options):
        with transaction.atomic():
            for name, permissions in self.setup_groups.items():
                group = Group.objects.filter(name=name).first() or Group.objects.create(name=name)
                group.permissions.clear()
                group.permissions.add(*Permission.objects.filter(codename__in=permissions))
