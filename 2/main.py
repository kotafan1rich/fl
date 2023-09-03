import datetime

from loguru import logger

from atomy_parser import ParserAtomypartners


logger.add("app.log", level="INFO")


def time_of_function(function):
    def wrapped(*args, **kwargs):
        start_time = datetime.datetime.now()
        res = function(*args, **kwargs)
        logger.info(
            f'Время выполнения программы - {datetime.datetime.now() - start_time}')
        return res
    return wrapped


@time_of_function
def main():
    url = 'http://atomypartners.ru/shop/'
    parser = ParserAtomypartners(url)
    parser.get_result()


if __name__ == '__main__':
    main()
