"""
Send notifications to Slack.

Thanks to
https://gist.github.com/devStepsize/b1b795309a217d24566dcc0ad136f784
"""

import json
import logging

import httpx
from django.conf import settings

from docurba.utils.enums import DocurbaEnvironment

logger = logging.getLogger(__name__)


def send_slack_message(
    text: str = "Hello world :wave:", url: str | None = None
) -> None:
    text = f"[{settings.DOCURBA_ENVIRONMENT}] {text}"
    url = url or settings.SLACK_TECH_MONITORING_URL
    if not url:
        if settings.DOCURBA_ENVIRONMENT in [
            DocurbaEnvironment.DEV,
            DocurbaEnvironment.TEST,
        ]:
            logger.info("=============================\nSlack message:")
            logger.info(text)
        return
    response = httpx.post(
        url=url,
        data=json.dumps({"text": text}),
        headers={"Content-Type": "application/json"},
    )
    if response.status_code != 200:  # noqa: PLR2004
        raise ValueError(
            (
                "Request to slack returned an error %s, the response is:\n %s",
                response.status_code,
                response.text,
            )
        )
