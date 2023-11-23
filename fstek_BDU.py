import functions
import pandas as pd
import re


def main():

    vul_link = f"https://bdu.fstec.ru/vul/{functions.num_url()}"

    driver = functions.open_msdriver()

    stoper = True
    source = "ФСТЭК"
    counter = 0

    df = pd.DataFrame(
        {"№": [""], "Источник": [""], "Дата публикации": [""], "CVE": [""], "CVSS": [""], "Продукты": [""], "Ссылки": [""]})

    while stoper:
        try:
            soup = functions.get_soup(driver, vul_link, None)

            tds = soup.find_all("td")

            product = tds[3].text.strip() + " " + tds[5].text.strip()

            print(f"Обрабатывается уязвимость {vul_link}")

            cvss = tds[23].text.strip()
            pattern = r"\d+(?:,\d+)?"
            number = re.findall(pattern, cvss)
            size = len(number) - 1
            cvss = number[size].replace(',', '.')

            cve = tds[39].text.strip()

            data = tds[19].text.strip()

            functions.pd_placeholder(df, counter, source, data, cve, cvss, product, vul_link)

            counter += 1
            
            vul_link = f"https://bdu.fstec.ru/vul/{functions.create_link(vul_link)}"

        except IndexError:
            if counter == 0:
                print("Ошибка ввода данных. Такая страница не найдена\n")
                vul_link = f"https://bdu.fstec.ru/vul/{functions.num_url()}"
                counter = 0
                pass
            else:
                stoper = False

    driver.close()

    functions.do_excel(source, df)

    input()


main()
