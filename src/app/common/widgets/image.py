from django import forms
from django.contrib.admin.widgets import AdminURLFieldWidget


class ImageInputMixin:
    css_class = ""

    def __init__(self, attrs=None, *, css_class=None):
        super().__init__(attrs)
        self.css_class = css_class or getattr(self, "css_class", "")

    def get_context(self, name, value, attrs):
        context = super().get_context(name, value, attrs)
        context["widget"]["class"] = self.css_class
        return context

    @property
    def media(self):
        return super().media + forms.Media(
            css={
                "screen": ("admin/css/image.css",),
            }
        )


class ImageInput(ImageInputMixin, forms.ClearableFileInput):
    template_name = "admin/widgets/image.html"


class ImageWidget(ImageInput):
    template_name = "admin/widgets/image_readonly.html"

    @classmethod
    def instance(cls, css_class=""):
        return type(cls.__name__, (cls,), {"read_only": True, "css_class": css_class})


class ImageURLInput(ImageInputMixin, AdminURLFieldWidget):
    template_name = "admin/widgets/image_url.html"
