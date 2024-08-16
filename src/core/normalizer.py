import phonenumbers
from phonenumbers import NumberParseException


class NormalizePhoneNumber:
    @staticmethod
    def _parse(phone: str) -> phonenumbers.PhoneNumber:
        try:
            _instance = phonenumbers.parse(
                number=phone, region=None, _check_region=False
            )
            if not phonenumbers.is_valid_number(_instance):
                raise NumberParseException(
                    error_type=NumberParseException.INVALID_COUNTRY_CODE,
                    msg="Invalid phone number",
                )
        except NumberParseException as e:
            raise ValueError(e)

        return _instance

    def try_is_phone(self, phone: str) -> str | None:
        try:
            return self.normalize(phone=phone)
        except ValueError:
            return None

    def normalize(self, phone: str, as_db: bool = False) -> str:
        # fix prefixes of phone number to national variants
        if phone.startswith("0"):
            phone = phone.replace("0", "+996", 1)
        elif phone.startswith("7"):
            phone = "+" + phone
        elif phone.startswith("8"):
            phone = "+7" + phone[1:]
        else:
            if not phone.startswith("+"):
                phone = "+" + phone

        try:
            phone_obj = self._parse(phone=phone)
        except ValueError:
            raise

        _format = (
            phonenumbers.PhoneNumberFormat.E164
            if as_db
            else phonenumbers.PhoneNumberFormat.NATIONAL
        )
        return phonenumbers.format_number(phone_obj, num_format=_format)
