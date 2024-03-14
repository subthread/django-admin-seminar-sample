from django.db import models
from django.forms import widgets


# <input type="color"> を実現する widgets.Widget
class ColorInput(widgets.Input):
    input_type = "color"
    template_name = "django/forms/widgets/input.html"
    read_only = True

    def __init__(self, attrs=None):
        super().__init__(attrs={**(attrs or {}), "style": "margin-right:10em"})

    def render(self, name, value, attrs=None, renderer=None):
        if not attrs:
            # readonly 対応
            attrs = {"disabled": True}
        return super().render(name, value, attrs, renderer)


# 色を管理する models.Field
class ColorField(models.CharField):
    def formfield(self, **kwargs):
        # forms.Field はスーパークラスが forms.CharField を指定してくれる
        return super().formfield(**{**kwargs, "widget": ColorInput})
