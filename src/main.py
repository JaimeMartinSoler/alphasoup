from page_generator import PageGenerator
from utils.config_loader import CONFIG
from utils.logger_builder import build_logger


def main():

    page_generator = PageGenerator(**CONFIG['global']['output'])
    page_generator.generate_pages()


if __name__ == '__main__':

    # logger
    build_logger(log_level=CONFIG['global']['log']['level'])

    # main()
    main()
