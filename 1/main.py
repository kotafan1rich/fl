import datetime
from loguru import logger

import relaticta_parser

logger.add("app.log", level="INFO")

URL = 'https://www.realitica.com/index.php?for=Prodaja&opa=Budva&type%5B%5D=&type%5B%5D=Apartment&price-min=30000&price-max=150000&since-day=p-anytime&qry=&lng=hr'

DOMAIN = 'https://www.realitica.com'


def time_of_function(function):
    def wrapped(*args):
        start_time = datetime.datetime.now()
        res = function(*args)
        logger.info(
            f'Время выполнения программы - {datetime.datetime.now() - start_time}')
        return res
    return wrapped


def write_res_in_file(res, file_name):
    file_name = 'result.txt' if not file_name else file_name
    if '.txt' not in file_name:
        file_name += '.txt'
    with open(file_name, 'w+', encoding='utf-8') as f:
        for url in res:
            f.write(f'{url}\n')
    logger.info(f'Сохранено - {file_name}')


@time_of_function
def main():
    file_name = input('Ведите имя файла, куда будет сохранён результат (без .txt): ')

    parser = relaticta_parser.ParserRealitica(url=URL, domain=DOMAIN)
    res = parser.get_result()
    write_res_in_file(res, file_name)



if __name__ == '__main__':
    main()
