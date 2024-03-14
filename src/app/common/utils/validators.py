from django.core.validators import FileExtensionValidator, MaxValueValidator
from django.template.defaultfilters import filesizeformat
from django.utils.deconstruct import deconstructible


class ImageFileValidator(FileExtensionValidator):
    allowed_extensions = ("png", "jpg", "jpeg")

    def __init__(self, message=None, code=None):
        super().__init__(allowed_extensions=ImageFileValidator.allowed_extensions, message=message, code=code)


@deconstructible
class MaxFileSizeValueValidator(MaxValueValidator):
    code = "max_file_size"

    @property
    def message(self):
        return f"{filesizeformat(self.limit_value)}以下のファイルを選択してください。"

    def clean(self, x):
        return super().clean(x).size
