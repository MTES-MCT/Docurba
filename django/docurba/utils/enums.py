import enum


class DocurbaEnvironment(enum.StrEnum):
    PROD = "PROD"
    DEMO = "DEMO"
    REVIEW_APP = "REVIEW-APP"
    TEST = "TEST"
    DEV = "DEV"
