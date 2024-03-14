from datetime import timedelta

from django import views
from django.http import FileResponse
from django.utils import timezone

from ..executors.archiver import ActivityArchiver


class RecentActivityArchiveView(views.View):
    def get(self, request):
        start_date = timezone.localdate().replace(day=1)
        end_date = (start_date + timedelta(days=40)).replace(day=1) - timedelta(days=1)
        archive = ActivityArchiver(start_date, end_date)
        filename = f"monthly_activity_{start_date.strftime('%Y%m%d')}.csv"

        # レスポンス
        response = FileResponse(archive, as_attachment=True, filename=filename)
        response.set_headers(None)  # archive.read() が無くて set_headers() が呼ばれないので自前で呼ぶ
        return response
