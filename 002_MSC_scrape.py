import os
import re
import sys
import argparse
import logging
import random
import datetime
import socket
from time import sleep
from logging.handlers import RotatingFileHandler
from bs4 import BeautifulSoup
from contextlib import closing
import selenium.common.exceptions as selexcept
from selenium.webdriver import Firefox
from selenium.webdriver.support.wait import WebDriverWait
# from pyvirtualdisplay import Display


def get_args():
    parser = argparse.ArgumentParser(
        description='Parse web site www.msc.com with country location USA'
    )
    parser.add_argument('-min', type=int, metavar='pause time in sec',
                        default=10,
                        help='Minimal time pause between requests to web site'
                             ' in seconds')
    parser.add_argument('-max', type=int, metavar='pause time in sec',
                        default=20,
                        help='Maximum time pause between requests to web site'
                             ' in seconds')
    parser.add_argument('-t', '--timeout', type=int, metavar='sec',
                        default=30,
                        help='Timeout')
    parser.add_argument('-f', '--config_file', type=str, metavar='file name',
                        default='002_MSC_config.txt',
                        help='Path to config file')
    parser.add_argument('-o', '--output', type=str, metavar='folder name',
                        default='latest',
                        help='Path to config file')
    parser.add_argument('-l', '--log_to_file', action='store_const', metavar='',
                        const=True,
                        help='Enable / disable logging to file')
    parser.add_argument('-w', '--weeks', type=int, metavar='result',
                        default=6, choices=[1, 2, 3, 4, 5, 6],
                        help='Time interval in weeks')
    return parser


def create_dir(dir_name):
    if not os.path.isdir(dir_name):
        try:
            os.makedirs(dir_name)
        except OSError as e:
            logger.error('OS error({0}): {1}'.format(e.errno, e.strerror))
            sys.exit(1)


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
    if switch:
        create_dir('logs')
        file_formatter = logging.Formatter(log_formatter)
        file_log = RotatingFileHandler('logs/MSC.log', mode='a',
                                       maxBytes=5*1024*1024, backupCount=2)
        file_log.setLevel(logging.DEBUG)
        file_log.setFormatter(file_formatter)
        logger.addHandler(file_log)


def get_text_fom_tag(line, left='>', right='<'):
    return re.findall('{0}(.*){1}'.format(left, right), str(line))[0]


def scrape_website(url, serch_url, serch_args, timeout):
    serch_url += '?fromPort={0}&toPort={1}&date={2}&weeks={3}&destination=' \
                 '{4}'.format(serch_args['from_port'], serch_args['to_port'],
                              serch_args['date'], serch_args['weeks'],
                              serch_args['destination'])
    logger.info('Grab URL: {0}'.format(serch_url))
    # Hide Firefox browser
    # Display(visible=0, size=(1024, 768)).start()
    try:
        with closing(Firefox()) as browser:
            browser.get(url)
            button = browser.find_element_by_id('lnkCookieAccept')
            button.click()
            browser.get(serch_url)
            WebDriverWait(browser, timeout).until(
                lambda s: s.execute_script("return jQuery.active == 0"))
    except (selexcept, socket.timeout) as e:
        logger.error(str(e))
        raise Exception('Something wrong', 'Error with selenium')
    soup = BeautifulSoup(browser.page_source, 'html.parser')
    vessels_list = soup.find_all('span', {'data-bind': 'text: VesselName'})
    # Checking if the resulting web page does not contain the necessary data
    if not vessels_list:
        raise Exception('Error', 'Incorrect input data: From port: {0}; '
                                 'To port: {1}; Date: {2}; Weeks: {3}'.format(
            serch_args['from_port'], serch_args['to_port'], serch_args['date'],
            serch_args['weeks']))
    voyage_number_list = soup.find_all('td', {'data-bind': 'text: VoyageNumber'})
    service_list = soup.find_all('td', {'data-bind': 'text: Service'})
    terminals_list = soup.find_all('td', {'data-bind': 'text: Terminal'})
    departure_list = soup.find_all('td', {
        'data-bind': "text: EstimatedDeparture.format('ddd, DD MMM YYYY')"})
    transit_time_list = soup.find_all('td', {
        'data-bind': 'text: TransitTimeInDaysText'})
    arrival_list = soup.find_all('td', {
        'data-bind': "text: EstimatedArrival.format('ddd, DD MMM YYYY')"})
    route = soup.find_all('h3', {'data-bind': 'text: PortsText()'})
    date = soup.find_all('span', {'data-bind': 'text: DateText()'})
    get_text_fom_tag(route)
    head = {'route': get_text_fom_tag(route), 'date': get_text_fom_tag(date)}
    result = {}
    for n in xrange(0, len(vessels_list)):
        result[get_text_fom_tag(vessels_list[n])] = {
            'voyage_number': get_text_fom_tag(voyage_number_list[n]),
            'service': get_text_fom_tag(service_list[n]),
            'terminal': get_text_fom_tag(terminals_list[n]),
            'departure': get_text_fom_tag(departure_list[n]),
            'transit': get_text_fom_tag(transit_time_list[n]),
            'arrival': get_text_fom_tag(arrival_list[n])}
    logger.info('Successfully grabbed data from URL')
    return head, result


def create_html(head, data):
    line = ''
    for key in data.keys():
        line += '<tr><td>{0}</td><td align="center">{1}</td>' \
                '<td align="center">{2}</td><td align="center">{3}</td>' \
                '<td align="center">{4}</td><td align="center">{5}</td>' \
                '<td align="center">{6}</td></tr>\n'.format(
            key, data[key]['voyage_number'], data[key]['service'],
            data[key]['terminal'], data[key]['departure'], data[key]['transit'],
            data[key]['arrival'])
    html_template = """<!DOCTYPE html>
<head>
<meta charset="utf-8">
<title>www.msc.com</title>
</head>
<body>
<h3>{0}</h3>
<h3>ROUTE:{1}</h3>
<hr>
<table width="100%" margin="auto">
<tr>
    <th>Vessel name</th>
    <th>Voyage number</th>
    <th>Service</th>
    <th>Terminal</th>
    <th>Departure date</th>
    <th>Transit</th>
    <th>Arrival date</th>
</tr>
{2}
</table>
</body>""".format(head['date'], head['route'], line)
    return html_template


def main():
    args = vars(get_args().parse_args())
    create_logging(args['log_to_file'])
    logger.info('#'*40 + ' START ' + '#'*40 + '\n')
    create_dir(args['output'])
    args['url'] = 'https://www.msc.com/usa'
    args['serch_url'] = 'https://www.msc.com/usa/help-centre/tools/' \
                        'search-schedules?'
    try:
        rdcf = open(args['config_file'], 'r')
    except IOError as e:
        logger.error('I/O error({0}): {1}. File: {2}'.format(
            e.errno, e.strerror, args['config_file']))
        sys.exit(1)
    for line in rdcf:
        if line.strip():
            date_today = datetime.date.today()
            for attempt in range(1, 3):
                html_file_name = '{0}.{1}.html'.format(
                    line.split(', ')[-1].replace(' ', '_').strip(), attempt)
                if attempt == 2:
                    date_today += datetime.timedelta(args['weeks'] * 7)
                args['serch_args'] = {
                    'from_port': line.split(', ')[0],
                    'to_port': line.split(', ')[1],
                    'date': date_today.strftime('%Y-%m-%d'),
                    'weeks': args['weeks'],
                    'destination': False}
                try:
                    head, data = scrape_website(
                        url=args['url'], serch_args=args['serch_args'],
                        serch_url=args['serch_url'],
                        timeout=args['timeout'])
                except Exception as e:
                    logger.error('{0}: {1}'.format(str(e[0]), str(e[1])))
                    continue
                try:
                    with open('{0}/{1}'.format(args['output'],
                                               html_file_name), 'w') as wr:
                        wr.write(create_html(head, data))
                except IOError as e:
                    logger.error('I/O error({0}): {1}. File: {2}'.format(
                        e.errno, e.strerror, '{0}/{1}'.format(args['output'],
                                                              html_file_name)))
                    continue
                logger.info('File {0} successfully created\n'.format(
                    html_file_name))
                sleep(random.randint(args['min'], args['max']))
    rdcf.close()
    logger.info('#'*40 + ' FINISH ' + '#'*40 + '\n')


if __name__ == '__main__':
    main()
