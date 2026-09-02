import pytest
from django.core.exceptions import ValidationError

from docurba.utils.password_validation import CnilCompositionPasswordValidator


class TestCnilCompositionPasswordValidator:
    def test_validate(self) -> None:
        # Good passwords.

        # lower + upper + special char
        assert CnilCompositionPasswordValidator().validate("!*pAssWOrD") is None
        # lower + upper + digit
        assert CnilCompositionPasswordValidator().validate("MYp4ssW0rD") is None
        # lower + upper + digit + special char
        assert CnilCompositionPasswordValidator().validate("M+p4ssW0rD") is None

        # Wrong passwords.

        expected_error = CnilCompositionPasswordValidator.HELP_MSG
        wrong_passwords = ["MYpAssWOrD", "myp4ssw0rd"]
        for password in wrong_passwords:
            with pytest.raises(ValidationError) as error:
                # Only lower + upper
                CnilCompositionPasswordValidator().validate(password)
            assert error.value.messages == [expected_error]
            assert error.value.error_list[0].code == "cnil_composition"

    def test_help_text(self) -> None:
        assert (
            CnilCompositionPasswordValidator().get_help_text()
            == CnilCompositionPasswordValidator.HELP_MSG
        )
