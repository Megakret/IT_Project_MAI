import logging

channel_log_handler = logging.FileHandler(f"channel_fetcher.log", mode="a")


def init_channel_logger():
    channel_log_formatter = logging.Formatter(
        "%(name)s %(asctime)s %(levelname)s %(message)s"
    )
    channel_log_handler.setFormatter(channel_log_formatter)
