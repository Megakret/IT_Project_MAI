import logging

admin_log_handler = logging.FileHandler(f"admin.log", mode="a")


def init_admin_logger():
    admin_log_formatter = logging.Formatter(
        "%(name)s %(asctime)s %(levelname)s %(message)s"
    )
    admin_log_handler.setFormatter(admin_log_formatter)
