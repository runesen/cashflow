"""Script containing helper functions."""
import logging
import colorlog


def init_logger(
    run_in_debug_mode: bool = False,
) -> logging.Logger:
    """Set up logger either in default or debug mode.

    Outputs are written to a log folder with a date stamp.
    """
    # Defining what should be written to log.
    log_format = (
        "%(asctime)s - "
        "%(name)s - "
        "%(funcName)s - "
        "%(levelname)s - "
        "%(message)s"
    )

    # Defining colors e.g. red for error and yellow for warning.
    bold_seq = "\033[1m"
    colorlog_format = f"{bold_seq} " + "%(log_color)s " + f"{log_format}"
    colorlog.basicConfig(format=colorlog_format)

    logger = logging.getLogger(__name__)

    # If running in debug mode, we should be able to see debug
    # statements. Otherwise the lowest level of resolution is "info".
    if run_in_debug_mode:
        logger.setLevel(logging.DEBUG)
    else:
        logger.setLevel(logging.INFO)

    return logger
