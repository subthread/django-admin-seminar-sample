from django import forms
from django.db import models
from django.template.defaultfilters import filesizeformat

from ..utils.validators import ImageFileValidator, MaxFileSizeValueValidator


# forms.ImageField の拡張クラス（forms.Field）
class ImageFileFormField(forms.ImageField):
    # widgets.Widget はスーパークラスが指定する widgets.ClearableFileInput をそのままう
    allowed_extensions = [f".{ext}" for ext in ImageFileValidator.allowed_extensions]
    default_validators = (ImageFileValidator(),)

    def widget_attrs(self, widget):
        return {**super().widget_attrs(widget), "accept": ",".join(self.allowed_extensions)}


# models.ImageField の拡張クラス（models.Field）
class ImageFileField(models.ImageField):
    def __init__(self, *args, max_file_size=None, **kwargs):
        if max_file_size is not None:
            kwargs.setdefault("validators", []).append(MaxFileSizeValueValidator(max_file_size))
            if "help_text" not in kwargs:
                kwargs["help_text"] = f"{filesizeformat(max_file_size)}以内の画像ファイル（PNG/JPEG）を指定してください。"
        super().__init__(*args, **kwargs)

    def formfield(self, **kwargs):
        # forms.Field をカスタマイズしたクラスに差し替える
        return super().formfield(form_class=ImageFileFormField, **kwargs)
