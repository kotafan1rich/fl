import datetime
from loguru import logger
import sys
import argparse

import relaticta_parser

logger.add("app.log", level="INFO")

URL = 'https://www.realitica.com/index.php?for=Prodaja&opa=Budva&type%5B%5D=&type%5B%5D=Apartment&price-min=30000&price-max=150000&since-day=p-anytime&qry=&lng=hr'

DOMAIN = 'https://www.realitica.com'
DEFAULT_FILENAME = 'result.txt'


def time_of_function(function):
    def wrapped(*args, **kwargs):
        start_time = datetime.datetime.now()
        res = function(*args, **kwargs)
        logger.info(
            f'Время выполнения программы - {datetime.datetime.now() - start_time}')
        return res
    return wrapped


def create_parser():
    parser = argparse.ArgumentParser()
    parser.add_argument('-f', '--filename', default=DEFAULT_FILENAME)
    parser.add_argument('-u', '--url', default=URL)
    parser.add_argument('-d', '--domain', default=DOMAIN)

    return parser

def write_res_in_file(res, file_name):
    file_name = 'result.txt' if not file_name else file_name
    if '.txt' not in file_name:
        file_name += '.txt'
    with open(file_name, 'w+', encoding='utf-8') as f:
        for url in res:
            f.write(f'{url}\n')
    logger.info(f'Сохранено - {file_name}')


@time_of_function
def main(filename, url, domain):
    parser_relatica = relaticta_parser.ParserRealitica(url=url, domain=domain)
    res = parser_relatica.get_result()
    write_res_in_file(res, filename)



if __name__ == '__main__':
    parser = create_parser()
    namespace = parser.parse_args(sys.argv[1:])

    file_name = namespace.filename
    url = namespace.url
    domain = namespace.domain

    main(filename=file_name, url=url, domain=domain)
