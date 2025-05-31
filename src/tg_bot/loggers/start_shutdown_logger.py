import logging

start_shutdown_log_handler = logging.FileHandler(f"start_shutdown.log", mode="a")


def init_start_shutdown_logger():
    start_shutdown_formatter = logging.Formatter(
        "%(name)s %(asctime)s %(levelname)s %(message)s"
    )
    start_shutdown_log_handler.setFormatter(start_shutdown_formatter)