import functions
import time
from datetime import datetime
import re

date_input = input('Введите первую дату в формате DD.MM.YYYY: ')

try:
    date1 = datetime.strptime(date_input, '%d.%m.%Y').date()
except ValueError:
    print('Ошибка: Неверный формат введенной даты.')
    exit()

driver = functions.open_msdriver()
driver.minimize_window()

with open('utilities/rss.txt', 'r') as f:
    lines = [line.rstrip() for line in f]

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
                print(f'Первая дата ({date_input}) младше или равна второй дате ({formatted_date}).')

                link_tg = item.find("link")
                link = link_tg.next_sibling

                driver.get(link)

                cve_pattern = re.compile(r'CVE-\d{4}-\d{4,7}')
                cve_matches = soup.find_all(string=cve_pattern)

                if cve_matches:
                    cve = []
                    print('Найденные CVE:')
                    for match in cve_matches:
                        cve.append(re.findall(cve_pattern, match))
#   Нужно как-то убрать повторы в списке
#                    unique_cve = list(set(cve))
#                    print(unique_cve)

                else:
                    print('CVE не найдены на странице.')

            else:
                print(f'Первая дата ({date_input}) старше второй даты ({formatted_date}).')
    else:
        print(f'Ошибка: {url} не содержит "pubdate".')

driver.close()
