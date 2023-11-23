import time
import functions
import pandas as pd
import re


def main():
    num_pages = functions.num_pages()

    driver = functions.open_msdriver()
    driver.minimize_window()

    source = "НКЦКИ"
    counter = 0

    df = pd.DataFrame(
        {"№": [""], "Источник": [""], "Дата публикации": [""], "CVE": [""], "CVSS": [""], "Продукты": [""], "Ссылки": [""]})

    for page in range(1, num_pages + 1):
        soup = functions.get_soup(driver, "https://safe-surf.ru/specialists/bulletins-nkcki/?PAGEN_1=", page)
        time.sleep(2)

        print(f"{page} страница НКЦКИ обрабатывается...")

        links = [elem.get("href") for elem in soup.find_all("a", title="Подробнее")]

        vul_link = ["https://safe-surf.ru" + link for link in links]

        problem_data = [elem.get_text().strip().replace("Дата бюллетеня", "") for elem in
                        soup.find_all(class_="cell-bulletin-nkcki cell-1")]
        problem_data = list(filter(bool, problem_data))
        data = [elem.lstrip() for elem in problem_data]

        problem_cve = [elem.get_text().strip().replace("Идентификатор уязвимости", "") for elem in
                       soup.find_all(class_="cell-bulletin-nkcki cell-2")]
        problem_cve = list(filter(bool, problem_cve))
        problem_cve = [elem.lstrip() for elem in problem_cve]
        cve = [elem.strip().replace("MITRE:", "") for elem in problem_cve]

        problem_product = [elem.get_text().strip().replace("Уязвимый продукт", "") for elem in
                           soup.find_all(class_="cell-bulletin-nkcki cell-3")]
        problem_product = list(filter(bool, problem_product))
        problem_product = [elem.lstrip() for elem in problem_product]
        problem_product = [elem.replace("\n", "") for elem in problem_product]
        product = [re.sub(
            "                                                                                                                                 ",
            "     ", elem) for elem in problem_product]

        problem_cvss = [elem.get_text().strip().replace("Уровень опасности", "") for elem in
                        soup.find_all(class_="cell-bulletin-nkcki cell-4")]
        problem_cvss = list(filter(bool, problem_cvss))
        problem_cvss = [elem.lstrip() for elem in problem_cvss]
        problem_cvss = [elem.replace("\n", "") for elem in problem_cvss]
        print(problem_cvss)
        cvss = [re.sub("\\s+", " ", elem) for elem in problem_cvss]

        for i in range(len(links)):
            functions.pd_placeholder(df, counter, source, data[i], cve[i], cvss[i], product[i], vul_link[i])
            counter += 1

    driver.close()

    functions.do_excel(source, df)

    input()

main()
