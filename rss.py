import functions
import time
from datetime import datetime
import pandas as pd
import re
import feedparser
from urllib.parse import urlparse
import os.path
import html


def do_table(counter, source, formatted_date, str_cve, title, link, df):
    df.at[counter, '№'] = counter + 1
    df.at[counter, 'Источник'] = source
    df.at[counter, 'Дата публикации'] = formatted_date
    df.at[counter, 'CVE'] = str_cve
    df.at[counter, 'Заголовок'] = title
    df.at[counter, 'Ссылки'] = link
    return df


def is_valid_url(url):
    try:
        result = urlparse(url)
        return all([result.scheme, result.netloc])
    except ValueError:
        return False


def main():
    date1 = functions.find_date()

    driver = functions.open_msdriver()
    driver.minimize_window()

    file_path = 'utilities/rss.txt'
    if os.path.exists(file_path):
        print(f'Список порталов расположен в файле <{file_path}>')
    else:
        print(f'Файл со списком RSS порталов ОТСУТСТВУЕТ <{file_path}>')
        return 0

    with open(file_path, 'r') as f:
        lines = [line.rstrip() for line in f]

    counter = 0
    df = pd.DataFrame(
        {'№': [''], 'Источник': [''], 'Дата публикации': [''], 'CVE': [''], 'Заголовок': [''], 'Ссылки': ['']})

    for url in lines:
        result_str = url.replace('www.', '')
        match = re.search(r'//(.+?)/', result_str)
        if match:
            source = match.group(1)
        else:
            source = 'NEWS'

        if is_valid_url(url):
            driver.get(url)
            page_source = driver.page_source
            page_source = html.unescape(page_source)
            time.sleep(2)
            try:
                print(f'Обработка портала {source} начата')
                feed = feedparser.parse(page_source)
                if feed.entries:
                    for entry in feed.entries:
                        pub_date = entry.published
                        if pub_date != '':
                            try:
                                date_object = datetime.strptime(pub_date, '%a, %d %b %Y %H:%M:%S %z').date()
                            except ValueError:
                                date_object = datetime.strptime(pub_date, '%a, %d %b %Y %H:%M:%S %Z').date()

                        formatted_date = date_object.strftime('%d.%m.%Y')

                        if date1 <= date_object:

                            link = entry.link
                            title = entry.title
                            soup = functions.get_soup(driver, link, None)
                            cve_pattern = re.compile(r'CVE-\d{4}-\d{4,7}')
                            cve_matches = soup.find_all(string=cve_pattern)

                            if cve_matches:
                                for match in cve_matches:
                                    cve = re.findall(cve_pattern, match)
                                    str_cve = ' '.join(set(cve))
                                    lst = str_cve.split()

                                for l in lst:
                                    do_table(counter, source, formatted_date, l, title, link, df)
                                    counter += 1
                                    output_info = f'{formatted_date}: {l}: {link}'
                                    output_info = output_info.replace('\n', '').replace('\t', '')
                                    print(output_info)
                            else:
                                output_info = f'{formatted_date}: CVE Отсутствует: {link}'
                                output_info = output_info.replace('\n', '').replace('\t', '')
                                print(output_info)
                    print(f'Обработка портала {source} завершена')
                    print('-------------------------------------------------------------------------------------------------')
                else:
                    print(f'{url} не является RSS-лентой.')
                    print(f'Обработка портала {source} завершена')
                    print('-------------------------------------------------------------------------------------------------')
            except Exception as e:
                print(f'Ошибка при разборе страницы: {e}')

    driver.close()

    if counter != 0:
        functions.do_excel('NEWS', df)
    else:
        print('Новостей нет')

    input()


main()
