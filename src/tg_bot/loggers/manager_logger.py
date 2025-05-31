import logging

manager_log_handler = logging.FileHandler(f"manager.log", mode="a")


def init_manager_logger():
    manager_log_formatter = logging.Formatter(
        "%(name)s %(asctime)s %(levelname)s %(message)s"
    )
    manager_log_handler.setFormatter(manager_log_formatter)
