import phonenumbers


class NormalizePhoneNumber:
    @staticmethod
    def _parse(phone: str) -> phonenumbers.PhoneNumber:
        try:
            _instance = phonenumbers.parse(
                number=phone, region=None, _check_region=False
            )
            if not phonenumbers.is_valid_number(_instance):
                raise phonenumbers.NumberParseException
        except phonenumbers.NumberParseException as e:
            raise ValueError(e)

        return _instance

    def normalize(self, phone: str, as_db: bool = False) -> str:
        # fix prefixes of phone number to national variants
        if phone.startswith("0"):
            phone = phone.replace("0", "+996", 1)
        elif phone.startswith("7"):
            phone = "+" + phone
        else:
            if not phone.startswith("+"):
                phone = "+" + phone

        try:
            phone_obj = self._parse(phone=phone)
        except ValueError:
            return "Unknown phone number"

        _format = (
            phonenumbers.PhoneNumberFormat.E164
            if as_db
            else phonenumbers.PhoneNumberFormat.NATIONAL
        )
        return phonenumbers.format_number(phone_obj, num_format=_format)
