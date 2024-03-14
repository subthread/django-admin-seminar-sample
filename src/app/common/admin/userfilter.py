from django.contrib import admin
from django.utils.html import format_html

from app.user.models import ServiceUser


class UserFilter(admin.SimpleListFilter):
    title = "ユーザー"
    parameter_name = "user"
    add_facets = False

    def lookups(self, request, model_admin):
        # 自前の Facets対応のため count を annotate しておく & 1件以上記録があるユーザーのみを表示する
        return ServiceUser.objects.all()

    def queryset(self, request, queryset):
        return queryset.filter(user_id=user_id) if (user_id := self.value()) else queryset

    def choices(self, changelist):
        yield {
            "selected": self.value() is None,
            "query_string": changelist.get_query_string(remove=[self.parameter_name]),
            "display": "全て",
        }
        template = "{name} ({count})" if self.add_facets else "{name}"
        for user in self.lookup_choices:
            lookup = user.id
            if (count := getattr(user, "count", None)) is None:
                count = "-"
            yield {
                "selected": self.value() == str(lookup),
                "query_string": changelist.get_query_string({self.parameter_name: lookup}),
                "display": format_html(
                    " ".join([('<img height="20" src="{icon}"/>' if user.icon_url else ""), template]),
                    icon=user.icon_url,
                    name=user.name,
                    count=count,
                ),
            }
