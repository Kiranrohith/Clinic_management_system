import logging

logger = logging.getLogger("clinic.scheduler")


def run_scheduler() -> None:
    logger.info("Background scheduler initialized.")
