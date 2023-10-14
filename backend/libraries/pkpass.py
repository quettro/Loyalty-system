import io
import math
import os

from django.conf import settings
from django.core.files.base import ContentFile
from PIL import Image, ImageDraw, ImageEnhance, ImageFont

from .passbook import Alignment, Barcode, Location, Pass, StoreCard


class PkPass:
    """
    PkPass - отвечает за генерацию файлов с расширением .pkpass.
    """
    def __init__(self, client, message=None):
        self.__client = client
        self.__wallet = client.wallet
        self.__message = message
        self.__review_link = settings.PKPASS_REVIEW_LINK
        self.__review_text = settings.PKPASS_REVIEW_TEXT
        self.__card_issuer_link = settings.PKPASS_CARD_ISSUER_LINK
        self.__card_issuer_text = settings.PKPASS_CARD_ISSUER_TEXT
        self.__web_service_url = settings.PKPASS_WEB_SERVICE_URL
        self.__pkpass_root = settings.PKPASS_ROOT
        self.__wwdr_root = settings.WWDR_ROOT

        """
        [client.numbers]
            - Номер карты клиента.
        [client.name]
            - Наименование карты клиента.
        [client.sex]
            - Пол клиента.
        [client.birthday]
            - Дата рождения клиента.
        [client.phone]
            - Номер телефона клиента.
        """
        self.__shortcodes = {
            '{% client.numbers %}': self.__client.numbers,
            '{% client.name %}': self.__client.name,
            '{% client.sex %}': self.__client.get_sex().label,
            '{% client.birthday %}': str(self.__client.birthday),
            '{% client.phone %}': self.__client.phone,
        }

        """
        [client.status]
            - Наименование статуса клиента.
        """
        if self.__client.status is None:
            self.__shortcodes.update({
                '{% client.status %}': 'Не установлено'
            })
        else:
            self.__shortcodes.update({
                '{% client.status %}': self.__client.status.name
            })

        if self.__wallet.is_type_discount:
            """
            [client.discount]
                - Скидка клиента.
            """
            self.__shortcodes.update({
                '{% client.discount %}': self.__client.discount,
            })

        elif self.__wallet.is_type_bonus:
            """
            [client.balance]
                - Баланс клиента.
            [client.cashback]
                - Кэшбэк клиента.
            """
            self.__shortcodes.update({
                '{% client.balance %}': self.__client.balance,
                '{% client.cashback %}': self.__client.cashback,
            })

        elif self.__wallet.is_type_chop:
            """
            [client.stamps]
                - Кол-во активных штампов у клиента.
            [client.rewards]
                - Кол-во наград у клиента.
            [client.brta]
                - Сколько осталось набрать штампов для получения награды.
            [wallet.expires_at]
                - Срок действия акции.
            """
            brta = self.__wallet.stamps - self.__client.a_stamps

            self.__shortcodes.update({
                '{% client.stamps %}': self.__client.a_stamps,
                '{% client.rewards %}': self.__client.a_rewards,
                '{% client.brta %}': brta,
                '{% wallet.expires_at %}': self.__wallet.expires_at,
            })

    def create(self):
        return self.__pass(self.__store())

    def __store(self):
        _store = StoreCard()

        if not self.__wallet.is_deleted:
            header_fields = self.__wallet.frontend.get('header_fields')
            primary_fields = self.__wallet.frontend.get('primary_fields')
            secondary_fields = self.__wallet.frontend.get('secondary_fields')
            auxiliary_fields = self.__wallet.frontend.get('auxiliary_fields')

            if header_fields:
                for item in header_fields:
                    item['value'] = self.__format_shortcodes(item['value'])
                    _store.addHeaderField(**item)
                    _store.headerFields[-1].textAlignment = Alignment.RIGHT

            if primary_fields:
                for item in primary_fields:
                    item['value'] = self.__format_shortcodes(item['value'])
                    _store.addPrimaryField(**item)

            if secondary_fields:
                for item in secondary_fields:
                    item['value'] = self.__format_shortcodes(item['value'])
                    _store.addSecondaryField(**item)

            if auxiliary_fields:
                for item in auxiliary_fields:
                    item['value'] = self.__format_shortcodes(item['value'])
                    _store.addAuxiliaryField(**item)
                    _store.auxiliaryFields[-1].textAlignment = Alignment.RIGHT

        if self.__message:
            _title = self.__wallet.backend['push']['title']
            _message = self.__format_shortcodes(self.__message)
            _store.addBackField('message', _message, _title)
            _store.backFields[-1].changeMessage = '%@'

        if not self.__wallet.is_deleted:
            back_fields = self.__wallet.backend.get('back_fields')

            if back_fields:
                for item in back_fields:
                    item['value'] = self.__format_shortcodes(item['value'])
                    _store.addBackField(**item)

            if self.__wallet.backend['is_use_feedback_system']:
                message = (
                    f'<a href="{self.__review_link}">'
                    f'{self.__review_text}</a>'
                )
                _store.addBackField('reviews', message, 'Ваш отзыв')

        if not self.__wallet.partner.tariff.is_white_label:
            message = (
                f'<a href="{self.__card_issuer_link}">'
                f'{self.__card_issuer_text}</a>'
            )
            _store.addBackField('web', message, 'Эмитент карты')

        return _store

    def __format_shortcodes(self, string):
        if '{%' in string and '%}' in string:
            for key, value in self.__shortcodes.items():
                if key in string:
                    string = string.replace(key, str(value))
        return string

    def __pass(self, store):
        _pass = Pass(store)

        _pass.passTypeIdentifier = self.__wallet.cert.p12_pass_type_identifier
        _pass.organizationName = self.__wallet.name
        _pass.description = self.__wallet.name
        _pass.teamIdentifier = self.__wallet.cert.p12_team_identifier
        _pass.webServiceURL = self.__web_service_url
        _pass.authenticationToken = str(self.__client.authentication_token)
        _pass.serialNumber = self.__client.numbers
        _pass.backgroundColor = self.__wallet.frontend['background_color']
        _pass.foregroundColor = self.__wallet.frontend['foreground_color']
        _pass.labelColor = self.__wallet.frontend['label_color']
        _pass.logoText = self.__wallet.frontend['logo_text']
        _pass.sharingProhibited = self.__wallet.backend['sharingProhibited']

        if not self.__wallet.is_deleted:
            _pass.barcode = self.__barcode()

            _pass.associatedStoreIdentifiers = self.__wallet.backend.get(
                'associatedStoreIdentifiers', [])

            if self.__wallet.is_use_push_for_geolocation:
                tariff = self.__wallet.partner.tariff

                if tariff.is_use_push_for_geolocation:
                    _pass.locations = self.__get_locations()

        _pass.addFile('icon@2x.png', self.__wallet.icon.open())
        _pass.addFile('logo@2x.png', self.__wallet.logotype.open())
        _pass.addFile('strip@2x.png', self.__get_strip())

        if not os.path.exists(self.__pkpass_root):
            os.makedirs(self.__pkpass_root)

        _filename = f'{self.__client.numbers}.pkpass'
        _path = self.__pkpass_root / _filename

        _pass.create(
            self.__wallet.cert.p12_cert_pem.path,
            self.__wallet.cert.p12_cert_key.path,
            self.__wwdr_root,
            self.__wallet.cert.p12_password,
            _path
        )

        return _path

    def __barcode(self):
        _barcode = {}
        _barcode['message'] = str(self.__wallet.uuid)
        _barcode['format'] = self.__wallet.frontend['barcode_format']

        if self.__wallet.frontend['is_show_the_number_card']:
            _barcode['altText'] = self.__client.numbers

        return Barcode(**_barcode)

    def __get_locations(self):
        return [
            Location(
                latitude=geolocation['latitude'],
                longitude=geolocation['longitude'],
                relevantText=geolocation['message']
            ) for geolocation in self.__wallet.geolocations
        ]

    def __get_strip(self):
        if self.__wallet.is_deleted:
            return self.__get_strip_is_deleted()

        if self.__wallet.is_type_chop:
            return self.__get_strip_is_type_chop()

        return self.__wallet.background_image.open()

    def __get_strip_is_type_chop(self):
        """ Отступы между штампами в px. """
        margin = 15

        """ Общее кол-во штампов для вывода. """
        count = self.__wallet.stamps

        """ Кол-во активных штампов клиента. """
        if self.__wallet.is_unlimited:
            active = self.__client.a_stamps
        else:
            active = self.__client.c_stamps

        """ Если есть лишние активные штампы, то удаляем их. """
        active = count if active > count else active

        """ Кол-во добавленных штампов. """
        added = 0

        """ Макс. кол-во штампов на одной линий. """
        max = settings.MAX_NUMBER_OF_STAMPS_PER_ONE_LINE

        """ Кол-во линий. """
        lines = math.ceil(count / max) if count > max else 1

        """ Фоновое изображение """
        background = Image.open(self.__wallet.background_image)

        """ Иконка активного штампа. """
        a_icon = Image.open(self.__wallet.active_stamp_icon)

        """ Чистый холст для вывода всех штампов. """
        stamps = Image.new(mode='RGBA', size=background.size)

        """
        Если партнер загрузил иконку неактивного штампа, то используем его,
        если не загружал, то берем активную иконку штампа и затемняем его.
        """
        if self.__wallet.nonactive_stamp_icon:
            na_icon = Image.open(self.__wallet.nonactive_stamp_icon)
        else:
            na_icon = Image.open(self.__wallet.active_stamp_icon)
            na_icon = ImageEnhance.Brightness(na_icon)
            na_icon = na_icon.enhance(0.2)

        """
        Если партнер загрузил финишную иконку штампа, то используем его,
        если не загружал, то используем неактивную иконку штампа.
        """
        if self.__wallet.finish_stamp_icon:
            f_icon = Image.open(self.__wallet.finish_stamp_icon)
        else:
            f_icon = na_icon

        """
        Чистые холсты для вывода штампов. На одном хосте выводится одна линия
        штампов.
        """
        cleans = []

        """
        В цикле начинаем накладывать иконки штампов на чистые холсты.
        """
        for line in range(lines):
            cleans.append({
                'object': Image.new(mode='RGBA', size=background.size),
                'count': 0,
                'position': [0, 0]
            })

            clean = cleans[line]

            for i in range(count - added):
                if clean['count'] >= max:
                    break

                added += 1

                clean['position'][0] = i * a_icon.size[0] + i * margin
                clean['position'][1] = line * a_icon.size[1]

                if active > 0:
                    icon = a_icon
                else:
                    icon = f_icon if added >= count else na_icon

                clean['object'].paste(icon, tuple(clean['position']), icon)
                clean['count'] += 1

                active -= 1

            x = 0
            y = line * margin if lines > 1 else 0

            stamps.paste(clean['object'], (x, y), clean['object'])

        """
        Определяем какие отступы по краям должны быть, чтобы холст со штампами
        встал по центру фонового изображения.
        """
        center_x = background.size[0] - cleans[0]['position'][0]
        center_x = round((center_x - a_icon.size[0]) / 2)

        """
        В зависимости от кол-во линий определяем x и y.
        """
        if lines > 1:
            x = center_x
            y = ((a_icon.height * lines) + (margin * (lines - 1)))
            y = (background.height - y) // 2
        else:
            x = margin if count < max else center_x
            y = margin

        """
        Накладываем штампы на фоновое изображение.
        """
        background.paste(stamps, (x, y), stamps)

        """
        Проверяем, не безлимитная ли акция
        """
        if not self.__wallet.is_unlimited:
            """
            Проверяем, выводить ли сообщение о том, что награда получена.
            """
            if self.__wallet.is_message_about_bonus_received_displayed:
                """
                Если общее кол-во полученных штампов клиентом превышает
                кол-во штампов для получения награды, то получается клиент
                заполнил все штампы и получил награду. Соответственно для него
                акция закрыта и поверх фонового изображения отображаем
                соответствующее сообщение.
                """
                if self.__client.c_stamps >= self.__wallet.stamps:
                    message = settings.PKPASS_MESSAGE_IF_RECEIVED_REWARD

                    background = self.__apply_text_over_the_image(
                        background, message)

        buffer = io.BytesIO()
        background.save(fp=buffer, format='jpeg')

        return ContentFile(buffer.getvalue())

    def __get_strip_is_deleted(self):
        """
        Получить фоновое изображение, если карта была приостановлена.
        """
        message = settings.PKPASS_MESSAGE_IF_WALLET_IS_DELETED

        background = Image.open(self.__wallet.background_image)
        background = self.__apply_text_over_the_image(background, message)

        buffer = io.BytesIO()
        background.save(fp=buffer, format='jpeg')

        return ContentFile(buffer.getvalue())

    def __apply_text_over_the_image(self, image, message):
        """
        Наложить текст поверх изображения, так-же центруя его.
        """
        font = ImageFont.truetype(str(settings.PKPASS_FONT_FAMILY), size=48)

        image = ImageEnhance.Brightness(image)
        image = image.enhance(0.2)

        draw = ImageDraw.Draw(image)
        textsize = draw.textsize(message, font=font)

        x = (image.width - textsize[0]) / 2
        y = (image.height - textsize[1]) / 2

        draw.text((x, y), message, font=font, fill='#ffffff')

        return image
