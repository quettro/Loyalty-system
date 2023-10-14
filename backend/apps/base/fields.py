from django.core.exceptions import ValidationError
from django.db.models import ImageField
from PIL import Image


class LimitedImageField(ImageField):
    def __init__(self, *args, **kwargs):
        self.min_dim = kwargs.pop('min_dim', None)
        self.max_dim = kwargs.pop('max_dim', None)
        self.max_upload_size = kwargs.pop('max_upload_size', None)
        self.square = kwargs.pop('square', False)

        super().__init__(*args, **kwargs)

    def clean(self, *args, **kwargs):
        value = super().clean(*args, **kwargs)
        image = Image.open(value)
        width, height = image.size

        if self.max_upload_size:
            try:
                if (value.file.size / 1024) > self.max_upload_size:
                    raise ValidationError((
                        'Размер изображения превышает '
                        f'{self.max_upload_size} кб.'))
            except AttributeError:
                pass

        if self.min_dim:
            if width < self.min_dim[0] or height < self.min_dim[1]:
                raise ValidationError((
                    'Разрешение изображения не должно быть меньше, чем '
                    f'{self.min_dim[0]}x{self.min_dim[1]}'))

        if self.max_dim:
            if width > self.max_dim[0] or height > self.max_dim[1]:
                raise ValidationError((
                    'Разрешение изображения превышает '
                    f'{self.max_dim[0]}x{self.max_dim[1]}'))

        if self.square:
            if width != height:
                raise ValidationError((
                    'Ширина изображения не соответствует высоте, '
                    'изображение должно иметь квадратную форму.'))

        return value
