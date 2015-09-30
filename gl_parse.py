#! coding:utf-8
import re
import time
import bs4
import urllib2
import smtplib
import getpass
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

mail_login = 'tishyk@mail.ru'
mail_pass = getpass.getpass('Enter Passsword:')
target_address = ['srktest2015@gmail.com',mail_login]

page_addr = 'http://globallogic.com.ua/ru/positions/kyiv/'
page = urllib2.urlopen(page_addr)
page_data = page.read()

def content_wraper(func):
    html_view = '<li><a style="line-height: 18px; margin-left: 5px;margin-top: 3px; font-size: 15px; color: #105CB6;"'+\
    'href="{2}" title="Published date: {0}">{1}</a></li><br>'
    def wraper(page_data):
        html_code = '<html>\n<head></head>\n<body><ol>{0}</ol>\n</body></html>'
        modified_content ='\n'.join([html_view.format(*dtl) for dtl in func(page_data)])
        return html_code.format(modified_content)
    return wraper

@ content_wraper
def get_content(page_data):
    global content
    parsed_data = bs4.BeautifulSoup(page_data, "html.parser")
    res = parsed_data.body.findAll('a', attrs={'class':'cl-link'})
    content = []
    for r in res:
        link = r['href']
        title = r.find('h3').getText()
        Published = r.find('time')
        datePublished = Published['datetime']
        if '-09-' not in datePublished: continue
        if ('QA' or 'Test' or 'Automation') not in title: continue
        content.append([datePublished, title, link])
        
    return content

html_message = get_content(page_data)
text_message = '\n'.join(['{0}\t{1}\n{2}\n'.format(*line) for line in content])

msg = MIMEMultipart('alternative')
msg['Subject'] = "Global Logic Hot Vacancy Link"
msg['From'] = mail_login
msg['To'] = ';'.join(target_address)

# Record the MIME types of both parts - text/plain and text/html.
text_part = MIMEText(text_message, 'plain')
html_part = MIMEText(html_message, 'html')

# Attach parts into message container.
# According to RFC 2046, the last part of a multipart message, in this case
# the HTML message, is best and preferred.
msg.attach(text_part)
msg.attach(html_part)

smtpObj = smtplib.SMTP('smtp.mail.ru', 587) 
# In case of SSL connection smtplib.SMTP_SSL('smtp.mail.ru', 465)
smtpObj.starttls()
smtpObj.login(mail_login,mail_pass)
smtpObj.sendmail(mail_login,target_address,msg.as_string())

smtpObj.quit()
print 'Done!'