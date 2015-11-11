import logging


def setup_log_handlers():
    html_handler = logging.StreamHandler()
    html_handler.setLevel(logging.DEBUG)
    html_handler.setFormatter(logging.Formatter('%(asctime)s - %(name)s - %(ip)s - %(message)s'))
    http_logger = logging.getLogger('http')
    http_logger.addHandler(html_handler)

    worker_handler = logging.StreamHandler()
    worker_handler.setLevel(logging.DEBUG)
    worker_handler.setFormatter(logging.Formatter('%(asctime)s - %(name)s - %(message)s'))
    worker_logger = logging.getLogger('worker')
    worker_logger.addHandler(worker_handler)

    store_handler = logging.StreamHandler()
    store_handler.setLevel(logging.DEBUG)
    store_handler.setFormatter(logging.Formatter('%(asctime)s - %(name)s - %(message)s'))
    store_logger = logging.getLogger('store')
    store_logger.addHandler(store_handler)
