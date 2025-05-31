import logging

user_log_handler = logging.FileHandler(f"user.log", mode="a")


def init_user_logger():
    user_log_formatter = logging.Formatter(
        "%(name)s %(asctime)s %(levelname)s %(message)s"
    )
    user_log_handler.setFormatter(user_log_formatter)
