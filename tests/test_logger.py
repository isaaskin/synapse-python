import logging

from synapse.logger import ColorFormatter


def generate_log_record(level: int) -> logging.LogRecord:
    return logging.LogRecord(
        name="test_name",
        level=level,
        pathname="test_pathname",
        lineno=1,
        msg="test_msg",
        args=None,
        exc_info=None,
    )


def test_color_formatter_debug() -> None:
    format_string = "[%(levelname_color)s] [%(name)s] - %(message)s"
    formatter = ColorFormatter(format_string)

    assert (
        formatter.format(generate_log_record(logging.DEBUG))
        == "[\x1b[36mDEBUG\x1b[0m] [test_name] - test_msg"
    )


def test_color_formatter_info() -> None:
    format_string = "[%(levelname_color)s] [%(name)s] - %(message)s"
    formatter = ColorFormatter(format_string)

    assert (
        formatter.format(generate_log_record(logging.INFO))
        == "[\x1b[32mINFO\x1b[0m] [test_name] - test_msg"
    )


def test_color_formatter_warning() -> None:
    format_string = "[%(levelname_color)s] [%(name)s] - %(message)s"
    formatter = ColorFormatter(format_string)

    assert (
        formatter.format(generate_log_record(logging.WARNING))
        == "[\x1b[33mWARNING\x1b[0m] [test_name] - test_msg"
    )


def test_color_formatter_error() -> None:
    format_string = "[%(levelname_color)s] [%(name)s] - %(message)s"
    formatter = ColorFormatter(format_string)

    assert (
        formatter.format(generate_log_record(logging.ERROR))
        == "[\x1b[31mERROR\x1b[0m] [test_name] - test_msg"
    )


def test_color_formatter_critical() -> None:
    format_string = "[%(levelname_color)s] [%(name)s] - %(message)s"
    formatter = ColorFormatter(format_string)

    assert (
        formatter.format(generate_log_record(logging.CRITICAL))
        == "[\x1b[35mCRITICAL\x1b[0m] [test_name] - test_msg"
    )
