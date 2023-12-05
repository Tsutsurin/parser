import functions
import pandas as pd
import requests


def main():
    constant_link = f'https://www.zerodayinitiative.com/advisories/ZDI-'

    vul_link = constant_link + functions.zdi_url() + '/'

    driver = functions.open_msdriver()
    driver.minimize_window()

    all = []
    stoper = True
    source = 'ZDI'
    counter = 0

    df = pd.DataFrame(
        {'№': [''], 'Источник': [''], 'Дата публикации': [''], 'CVE': [''], 'CVSS': [''], 'Продукты': [''], 'Ссылки': ['']})

    while stoper:
        try:
            print(f'Обрабатывается уязвимость {vul_link}')

            soup = functions.get_soup(driver, vul_link, None)

            data = soup.find('data').text
            
            tbs = soup.find('tbody')

            for tb in tbs:
                all.append(tb.text)

            cve = all[0].replace('\n', '')

            cvss = all[2].replace('\n', '')

            product = all[4].replace('AFFECTED VENDORS', '').replace('\n', '') + ' ' + all[6].replace('AFFECTED PRODUCTS', '').replace('\n', '')

            functions.pd_placeholder(df, counter, source, data, cve, cvss, product, vul_link)

            counter += 1
            
            vul_link = constant_link + functions.create_link_fstek(vul_link) + '/'

        except IndexError:
            if counter == 0:
                print('Ошибка ввода данных. Такая страница не найдена\n')
                vul_link = constant_link + functions.zdi_url() + '/'
                counter = 0
                pass
            else:
                stoper = False

    driver.close()
    
    functions.do_excel(source, df)

    input()


main()
