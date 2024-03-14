from django.db import models


class ActivityChoices(models.TextChoices):
    DONE = "done", "した"
    NOT = "not", "しなかった"


class EatChoices(models.TextChoices):
    EAT = "eat", "食べた"
    NOT = "not", "食べなかった"


class ActivitySummary(models.Model):
    class Meta:
        db_table = "activity_summary"
        verbose_name = verbose_name_plural = "活動記録"

    class AdminMeta:
        menu_name = "日々の活動"
        display_order = 1

    target_date = models.DateField("対象日")
    user = models.ForeignKey("user.ServiceUser", on_delete=models.CASCADE, verbose_name="ユーザー")

    steps = models.IntegerField("歩数", null=True, blank=True)
    sleep_time = models.FloatField("睡眠時間", null=True, blank=True)
    gymnastics = models.CharField("アクティブ体操", null=True, blank=True, choices=ActivityChoices.choices)
    dental = models.CharField("歯磨き", null=True, blank=True, choices=ActivityChoices.choices)
    morning = models.CharField("朝食", null=True, blank=True, choices=EatChoices.choices)
    snack = models.CharField("間食", null=True, blank=True, choices=EatChoices.choices)

    note = models.TextField("メモ", null=True, blank=True)

    def __str__(self):
        return f"[{self.target_date.strftime('%Y-%m-%d')}] {self.user.name}"


class ActivityDetail(models.Model):
    class Meta:
        db_table = "activity"
        verbose_name = verbose_name_plural = "運動"

    summary = models.ForeignKey(ActivitySummary, on_delete=models.CASCADE, related_name="details", verbose_name="ユーザー")

    activity = models.CharField("運動内容")
    minutes = models.IntegerField("運動時間", null=True, blank=True)
    mets = models.FloatField("運動強度METs", null=True, blank=True)
    details = models.TextField("詳細", null=True, blank=True)

    def __str__(self):
        return f"{self.summary} - {self.activity}"
