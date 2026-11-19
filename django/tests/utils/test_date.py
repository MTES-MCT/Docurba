from datetime import date

from docurba.utils.date import end_of_day


def test_end_of_day() -> None:
    assert (
        end_of_day(date.fromisoformat("2012-01-01")).isoformat()
        == "2012-01-01T23:59:59.999999+01:00"
    )
    assert (
        end_of_day(date.fromisoformat("2012-07-01")).isoformat()
        == "2012-07-01T23:59:59.999999+02:00"
    )
