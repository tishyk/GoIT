import os
import re
import argparse
import logging
from logging.handlers import RotatingFileHandler
from bs4 import BeautifulSoup
from contextlib import closing
from selenium.webdriver import Firefox
from selenium.webdriver.support.wait import WebDriverWait
from pyvirtualdisplay import Display


def get_args():
    parser = argparse.ArgumentParser(
        description='Parse web site www.msc.com with country location USA'
    )
    parser.add_argument('-min', '--min_pause_time', type=int, metavar='sec',
                        default=10,
                        help='Minimal time pause between requests to web site'
                             ' in seconds')
    parser.add_argument('-max', '--max_pause_time', type=int, metavar='sec',
                        default=20,
                        help='Maximum time pause between requests to web site'
                             ' in seconds')
    parser.add_argument('-t', '--timeout', type=int, metavar='sec',
                        default=30,
                        help='Timeout')
    parser.add_argument('-f', '--config_file', type=str, metavar='path',
                        required=False,
                        help='Path to config file')
    parser.add_argument('-l', '--log_to_file', action='store_const', metavar='',
                        const=True,
                        help='Enable / disable logging to file')
    return parser


def create_dir(dir_name):
    if not os.path.isdir(dir_name):
        os.makedirs(dir_name)


def create_logging(switch):
    global logger
    log_formatter = '%(asctime)s - %(levelname)s - %(message)s'
    logger = logging.getLogger(__name__)
    logger.setLevel(logging.DEBUG)
    console_log = logging.StreamHandler()
    console_log.setLevel(logging.INFO)
    formatter = logging.Formatter(log_formatter)
    console_log.setFormatter(formatter)
    logger.addHandler(console_log)
    switch = True
    if switch:
        create_dir('logs')
        file_formatter = logging.Formatter(log_formatter)
        file_log = RotatingFileHandler('logs/MSC.log', mode='a',
                                       maxBytes=5*1024*1024, backupCount=2)
        file_log.setLevel(logging.DEBUG)
        file_log.setFormatter(file_formatter)
        logger.addHandler(file_log)


def get_text_fom_tag(line, left, right):
    return re.findall('{0}(.*){1}'.format(left, right), str(line))[0]


def scrape_website(url, serch_url, serch_args):
    serch_url = '{0}?fromPort={1}&toPort={2}&date={3}&weeks={4}&destination=' \
                '{5}'.format(serch_url, serch_args['from_port'],
                             serch_args['to_port'], serch_args['date'],
                             serch_args['weeks'], serch_args['destination'])
    # Display(visible=0, size=(1024, 768)).start()
    # with closing(Firefox()) as browser:
    #     xpath = '//*[@id="scheduleResults"]/div[2]/div/section[1]/table/tbody/tr[1]/td[8]/a'
    #     browser.get(url)
    #     button = browser.find_element_by_id('lnkCookieAccept')
    #     button.click()
    #     browser.get(serch_url)
    #     # wait for the page to load
    #     WebDriverWait(browser, timeout=10).until(
    #         lambda x: x.find_element_by_xpath(xpath))
    # logger.info(browser.page_source)
    soup = BeautifulSoup(open('base_htm.html', 'r'), 'html.parser')
    vessels_list = soup.find_all('span', {'data-bind': 'text: VesselName'})
    voyage_number_list = soup.find_all('td', {'data-bind': 'text: VoyageNumber'})
    service_list = soup.find_all('td', {'data-bind': 'text: Service'})
    terminals_list = soup.find_all('td', {'data-bind': 'text: Terminal'})
    departure_list = soup.find_all('td', {
        'data-bind': "text: EstimatedDeparture.format('ddd, DD MMM YYYY')"})
    transit_time_list= soup.find_all('td', {
        'data-bind': 'text: TransitTimeInDaysText'})
    arrival_list = soup.find_all('td', {
        'data-bind': "text: EstimatedArrival.format('ddd, DD MMM YYYY')"})
    route = soup.find_all('h3', {'data-bind': 'text: PortsText()'})
    date = soup.find_all('span', {'data-bind': 'text: DateText()'})
    get_text_fom_tag(route, '>', '<')
    result = {'route': get_text_fom_tag(route, '>', '<'),
              'date': get_text_fom_tag(date, '>', '<')}
    for n in xrange(0, len(vessels_list)):
        result[get_text_fom_tag(vessels_list, '>', '<')] = [
            {'voyage_number': get_text_fom_tag(voyage_number_list, '>', '<')},
            {'service': get_text_fom_tag(service_list, '>', '<')},
            {'terminal': get_text_fom_tag(terminals_list, '>', '<')},
            {'Departure': get_text_fom_tag(departure_list, '>', '<')},
            {'transit': get_text_fom_tag(transit_time_list, '>', '<')},
            {'arrival': get_text_fom_tag(arrival_list, '>', '<')}]
    return result


if __name__ == '__main__':
    args = vars(get_args().parse_args())
    create_logging(args['log_to_file'])
    args['url'] = 'https://www.msc.com/usa'
    args['serch_url'] = 'https://www.msc.com/usa/help-centre/tools/search-schedules?'
    args['serch_args'] = {
        'from_port': 'CNDLC',
        'to_port': 'FRLEH',
        'date': '2015-10-23',
        'weeks': '6',
        'destination': False
    }
    # https://www.msc.com/usa/help-centre/tools/search-schedules?
    # fromPort=CNDLC&
    # toPort=FRLEH&
    # date=2015-10-25&
    # weeks=6&
    # destination=False
    logger.info(args)
    data = scrape_website(url=args['url'], serch_args=args['serch_args'],
                          serch_url=args['serch_url'])
    print(data)
    logger.info('DONE')
