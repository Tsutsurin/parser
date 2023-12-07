import functions
import time
from datetime import datetime
import pandas as pd
import re


def main():
    date1 = functions.find_date()

    driver = functions.open_msdriver()
    driver.minimize_window()

    with open('utilities/rss.txt', 'r') as f:
        lines = [line.rstrip() for line in f]

    counter = 1
    source = 'NEWS'
    df = pd.DataFrame(
        {'№': [''], 'Источник': [''], 'Дата публикации': [''], 'CVE': [''], 'Ссылки': ['']})

    for url in lines:
        driver.get(url)
        time.sleep(2)
        soup = functions.get_soup(driver, url, None)

        if soup.find('pubdate'):
            items = soup.find_all('item')
            for item in items:
                pubdate = item.find('pubdate').text
                try:
                    date_object = datetime.strptime(pubdate, '%a, %d %b %Y %H:%M:%S %z').date()
                except ValueError:
                    date_object = datetime.strptime(pubdate, '%a, %d %b %Y %H:%M:%S %Z').date()

                formatted_date = date_object.strftime('%d.%m.%Y')

                if date1 <= date_object:
                    link_tg = item.find("link")
                    link = link_tg.next_sibling
                    print(f'Идет поиск CVE в {link}')

                    driver.get(link)
                    soup = functions.get_soup(driver, link, None)

                    cve_pattern = re.compile(r'CVE-\d{4}-\d{4,7}')
                    cve_matches = soup.find_all(string=cve_pattern)

                    if cve_matches:
                        for match in cve_matches:
                            cve = re.findall(cve_pattern, match)
                            str_cve = ' '.join(set(cve))

                        df.at[counter, '№'] = counter
                        df.at[counter, 'Источник'] = source
                        df.at[counter, 'Дата публикации'] = formatted_date
                        df.at[counter, 'CVE'] = str_cve
                        df.at[counter, 'Ссылки'] = link

                        counter += 1
                        print(f'На старице {link} найдены следующие CVE: {str_cve}')
                    else:
                        print(f'CVE на странице {link} не найдены.')

        else:
            print(f'Ошибка: {url} не содержит "pubdate".')

    functions.do_excel(source, df)

    driver.close()

    input()


main()
