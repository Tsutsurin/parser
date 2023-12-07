from selenium import webdriver
from selenium.webdriver.edge.service import Service
from selenium.webdriver.edge.options import Options
from bs4 import BeautifulSoup
from datetime import date
from datetime import datetime
import pandas as pd
import re


def get_soup(driver, url_input, page):
    if page is None:
        url = url_input
    else:
        url = f'{url_input}{page}'
    driver.get(url)
    html = driver.page_source
    return BeautifulSoup(html, 'lxml')


def get_url():
    while True:
        try:
            print('##################################################')
            print('Укажите ссылку на ФСТЭК.')
            input_url = input('[https://bdu.fstec.ru/vul]: ')
            pattern = r'^https://bdu.fstec.ru/vul'
            if re.match(pattern, input_url):
                if re.search(r'&page=', input_url):
                    input_url = re.search(r'.*&page=', input_url)
                    return input_url.group()
                else:
                    return input_url + '+&page='
            else:
                print('Ошибка ввода данных. Следуйте примеру.\n')
        except ValueError:
            print('Неизвестная ошибка. Попробуйте следовать примеру.')


def num_pages():
    while True:
        try:
            input_number = int(input('Сколько страниц нужно просмотреть? '))
            if input_number < 0:
                print('Введено отрицательное число, попробуйте еще раз.')
            elif input_number > 200:
                print('Слишком большое число. Максимум 200.')
            else:
                return input_number
        except ValueError:
            print('Ошибка ввода. Ожидались цифры.')


def find_date():
    while True:
        print('##################################################')
        print('По какое число искать новости?')
        date_input = input('Пример [DD.MM.YYYY]: ')

        try:
            return datetime.strptime(date_input, '%d.%m.%Y').date()
        except ValueError:
            print('Ошибка: Неверный формат введенной даты.')


def zdi_url():
    while True:
        try:
            print('##################################################')
            print('Укажите id уязвимости для начала обработки информации.')
            input_url = input('[Пример 23-0000]: ')
            pattern = r'\d{2}-\d{4}'
            if re.match(pattern, input_url):
                return input_url
            else:
                print('Ошибка ввода данных. Следуйте примеру.\n')
        except ValueError:
            print('Неизвестная ошибка. Попробуйте следовать примеру.')


def create_link_fstek(vul_link):
    year = int(re.findall(r'\d{2}', vul_link)[0])
    number = int(re.findall(r'\d{4}', vul_link)[0]) + 1
    while len(str(number)) < 4:
        number = f'0{number}'
    vul_link = f'{year}-{number}'
    return vul_link


def num_url():
    while True:
        try:
            print('##################################################')
            print('Укажите id уязвимости для начала обработки информации.')
            input_url = input('[Пример 2023-00000]: ')
            pattern = r'\d{4}-\d{5}'
            if re.match(pattern, input_url):
                return input_url
            else:
                print('Ошибка ввода данных. Следуйте примеру.\n')
        except ValueError:
            print('Неизвестная ошибка. Попробуйте следовать примеру.')


def create_link(vul_link):
    year = int(re.findall(r'\d{4}', vul_link)[0])
    number = int(re.findall(r'\d{5}', vul_link)[0]) + 1
    while len(str(number)) < 5:
        number = f'0{number}'
    vul_link = f'{year}-{number}'
    return vul_link


def cvss_edited(cvss):
    try:
        pattern = r'\d+(?:.\d+)?'
        number = re.findall(pattern, cvss)
        if float(number[0]) < 4:
            return f'{number[0]} Low'
        elif float(number[0]) < 7:
            return f'{number[0]} Medium'
        elif float(number[0]) < 9:
            return f'{number[0]} High'
        else:
            return f'{number[0]} Critical'
    except Exception:
        return '-----'


def cve_edited(cve):
    try:
        matches = re.findall(r'CVE-\d{4}-\d{4,}', cve)
        if matches:
            match = matches[0]
            return match
        else:
            return '-----'
    except Exception:
        return '-----'


def do_excel(name, df):
    today = date.today()
    today = today.strftime('%d-%m-%Y')
    with pd.ExcelWriter(f'{today} {name}.xlsx') as writer:
        df.to_excel(writer, index=False)
        print(f'Ежедневный отчет {today}.xlsx создан.')


def open_msdriver():
    try:
        service = Service(r'utilities/msedgedriver.exe')
        options = Options()
        options.add_argument('disable-blink-features=AutomationControlled')
        options.add_argument('disable-infobars')
        options.add_argument('start-maximized')
        options.add_argument('ignore-certificate-errors')
        options.add_argument('log-level=3')
        return webdriver.Edge(options=options, service=service)
    except Exception:
        input('Ошибка. Обновите драйвер в папке "utilities".')


def open_driver():
    try:
        options = Options()
        options.add_argument('disable-blink-features=AutomationControlled')
        options.add_argument('disable-infobars')
        options.add_argument('start-maximized')
        options.add_argument('ignore-certificate-errors')
        options.add_argument('log-level=3')
        return webdriver.Chrome(options=options)
    except Exception:
        input('Ошибка открытия Chrome')


def pd_placeholder(df, counter, source, data, cve, cvss, product, vul_link):
    df.at[counter, '№'] = counter + 1
    df.at[counter, 'Источник'] = source
    df.at[counter, 'Дата публикации'] = data
    df.at[counter, 'CVE'] = cve_edited(cve)
    df.at[counter, 'CVSS'] = cvss_edited(cvss)
    df.at[counter, 'Продукты'] = product
    df.at[counter, 'Ссылки'] = vul_link
    return df
