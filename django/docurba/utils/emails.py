from django.conf import settings
from django.core import mail

from docurba.utils.enums import DocurbaEnvironment


class SendgridEmailMessage(mail.EmailMessage):
    def __init__(
        self,
        template_id: str,
        template_context: dict | None = None,
        *args,  # noqa: ANN002
        **kwargs,  # noqa: ANN003
    ) -> None:
        prefix = (
            ""
            if settings.DOCURBA_ENVIRONMENT == DocurbaEnvironment.PROD
            else f"(Test en {settings.DOCURBA_ENVIRONMENT.label}) "
        )
        self.dynamic_template_data = {
            "subject_preposition": prefix,
            **template_context,
        }
        self.template_id = template_id
        super().__init__(*args, **kwargs)


def get_email_message(  # noqa: PLR0917
    to: list,
    from_email: str = settings.DEFAULT_FROM_EMAIL,
    template_context: dict | None = None,
    template_id: str | None = None,
    bcc: list | None = None,
    cc: list | None = None,
) -> SendgridEmailMessage:
    # NOTE(cms): we should have a raw text alternative to read the email body in the console on dev mode
    # when SENDGRID_API_KEY is not set. But every email has been configured in Sendgrid as templates and it would be
    # a development too big to implement this alternative right now.
    return SendgridEmailMessage(
        from_email=f"L'équipe Docurba <{from_email}>",
        reply_to=[from_email],
        to=to,
        cc=cc,
        bcc=bcc,
        template_context=template_context,
        template_id=template_id,
    )
