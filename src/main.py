import datetime
import os
import shutil
from logging import config, getLogger
from selenium import webdriver
from selenium.common import NoSuchElementException, InvalidSelectorException
from selenium.webdriver.chrome.service import Service as ChromeService
from selenium.webdriver.common.by import By
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.chrome.options import Options

from common import set_common, set_log

common_conf = set_common()
TARGET_URL = common_conf['TARGET_URL']
BLOG_DIR = common_conf["BLOG_DIR"]

log_conf = set_log()
config.dictConfig(log_conf)
logger = getLogger(__name__)


def get_months(dr):
    logger.info('Start.')

    xpath = r'//*[@id="monthly-list"]/div[2]/ul/li[{}]/a'
    urs = []
    i = 0
    while True:
        i += 1
        try:
            elm = dr.find_element(By.XPATH, xpath.format(str(i)))
        except NoSuchElementException as e:
            logger.warning(e)
            break

        elm.click()
        urs.append(dr.current_url)
        logger.info('Got month. ({})'.format(dr.current_url))
        
        dr.get(TARGET_URL)

    logger.info('End.')
    return urs


def make_date(date):
    year = int(date[0:4])
    month = int(date[5:7])
    day = int(date[8:10])

    date = datetime.date(year, month, day)
    month_name = date.strftime("%B")

    return str(year), month_name, str(day)


def get_entry(dr, i_entry):
    xpath = r'//*[@class="entry"][{}]'.format(str(i_entry))

    elm = dr.find_element(By.XPATH, xpath)
    entry_id = elm.get_attribute('id')

    xpath = r'//*[@id="' + entry_id + '"]'
    elm = dr.find_element(By.XPATH, xpath + r'/table/tbody/tr/td/div')
    title = elm.text

    try:
        elm = dr.find_element(By.XPATH, xpath + r'/div/a')
    except NoSuchElementException:
        logger.warning('Getting Path (' + xpath + r'/div/p[1]/a')
        elm = dr.find_element(By.XPATH, xpath + r'/div/p[1]/a')
    url_mp3 = elm.get_attribute('href')

    try:
        elm = dr.find_element(By.XPATH, xpath + r'/div')
    except NoSuchElementException:
        logger.warning('Getting Path (' + xpath + r'/div/p[2]/a')
        elm = dr.find_element(By.XPATH, xpath + r'/div/p[2]/a')
    summary = elm.text.replace('\n', '')

    return entry_id, title, url_mp3, summary


def make_tags(year, month_name, title):
    vol = title.replace('石川・ホンマ・ぶるんのBe-SIDE Your Life! ', '')
    vol = vol[:-2]

    return [year, month_name + ' ' + year, vol]


def make_entry(day, month_name, summary, title, url_mp3, vol, year):
    entry = '---\n' \
            'title: ' + title + '\n' \
            'date: ' + month_name + ' ' + day + ', ' + year + '\n' \
            'tags: [\'' + year + '\', \'' + month_name + ' ' + year + '\', \'' + vol + '\']' + '\n' \
            'draft: false\n' \
            'summary: ' + summary + '\n' \
            '---\n' \
            '\n' + url_mp3

    return entry


def is_last_entry(dr, i_entry, title):
    xpath = r'//div[@class="entry"][{}]/following-sibling::node()[6]'.format(i_entry)
    try:
        elm = dr.find_element(By.XPATH, xpath)
        tag_name = elm.tag_name
        if tag_name != 'h2':
            return False
        elif title[-2:] == '-1':
            return True
        else:
            return False
    except NoSuchElementException as e:
        logger.warning(e)
        return False
    except InvalidSelectorException as e:
        logger.warning(e)
        return False


def get_month(dr, ents, ur):
    dr.get(ur)
    logger.info('URL: ' + url)

    i_date = 0
    i_entry = 0
    xpath = r'//*[@id="content"]/h2[{}]'
    while True:

        try:
            i_date += 1
            elm = dr.find_element(By.XPATH, xpath.format(str(i_date)))
        except NoSuchElementException as e:
            logger.warning(e)
            break

        date = elm.text
        year, month_name, day = make_date(date)

        while True:
            logger.info('Getting ' + date + '(Entry count (' + str(i_entry) + ')')

            try:
                i_entry += 1
                entry_id, title, url_mp3, summary = get_entry(dr, i_entry)
                logger.info('Got entry ID: ' + entry_id + ' (Title: ' + title + ')')
            except NoSuchElementException as e:
                logger.warning(e)
                logger.info('Got ' + date)
                break

            tags = make_tags(year, month_name, title)
            entry = make_entry(day, month_name, summary, title, url_mp3, tags[2], year)

            ents[entry_id] = entry

            if is_last_entry(driver, i_entry, title):
                logger.info('Got ' + date)
                break
            else:
                continue

    return ents


def make_markdowns(ents):
    for k, v in ents.items():
        filename = k + '.md'
        with open(BLOG_DIR + filename, 'w', encoding='utf-8') as file:
            file.write(v)


if __name__ == '__main__':
    logger.info('Start.')

    # blogフォルダ内を空にする。
    try:
        shutil.rmtree(BLOG_DIR)
    except FileNotFoundError as error:
        logger.warning(error)
    finally:
        os.mkdir(BLOG_DIR)

    # HPにアクセスする。
    options = Options()
    options.add_argument('--headless')
    driver = webdriver.Chrome(service=ChromeService(ChromeDriverManager().install()), options=options)
    driver.get(TARGET_URL)

    try:
        # 新しい順にすべての月urlを取得する。
        urls = get_months(driver)

        # 各月にアクセスする。
        entries = {}
        # for url in urls:
        for url in urls:
            # 各月にアクセスする。
            entries = get_month(driver, entries, url)

        # MDを作成する。
        make_markdowns(entries)

    except Exception as error:
        logger.critical(error)

    finally:
        # 処理を終了する
        driver.quit()
        logger.info('Finish.')
