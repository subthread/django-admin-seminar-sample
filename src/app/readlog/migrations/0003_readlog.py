# Generated by Django 5.0.1 on 2024-03-10 07:16

import django.db.models.deletion
import django.utils.timezone
from django.conf import settings
from django.db import migrations, models

import app.common.fields.color


class Migration(migrations.Migration):
    dependencies = [
        ("readlog", "0002_bibliographic_picture_bibliographic_sample"),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name="ReadLog",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                (
                    "created_at",
                    models.DateTimeField(default=django.utils.timezone.localtime, editable=False, verbose_name="登録日時"),
                ),
                ("updated_at", models.DateTimeField(auto_now=True, verbose_name="更新日時")),
                ("read_at", models.DateField(default=django.utils.timezone.localdate, verbose_name="読了日")),
                ("impression", models.TextField(blank=True, null=True, verbose_name="感想")),
                ("text_color", app.common.fields.color.ColorField(blank=True, default="#000000", verbose_name="文字色")),
                (
                    "background_color",
                    app.common.fields.color.ColorField(blank=True, default="#ffffff", verbose_name="背景色"),
                ),
                (
                    "book",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE, to="readlog.bibliographic", verbose_name="書籍"
                    ),
                ),
                (
                    "user",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL, verbose_name="ユーザー"
                    ),
                ),
            ],
            options={
                "verbose_name": "読書ログ",
                "verbose_name_plural": "読書ログ",
                "db_table": "readlog",
            },
        ),
    ]
