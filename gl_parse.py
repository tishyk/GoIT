#! coding:utf-8
import re
import time
import bs4
import urllib2

page_addr = 'http://globallogic.com.ua/ru/positions/kyiv/'

page = urllib2.urlopen(page_addr)
page_data = page.read()
parsed_data = bs4.BeautifulSoup(page_data, "html.parser")
res = parsed_data.body.findAll('a', attrs={'class':'cl-link'})

for r in res:
    #print str(r).decode('utf-8')
    link = r['href']
    title = r.find('h3').getText()
    Published = r.find('time')
    datePublished = Published['datetime']
    if '-09' not in datePublished: continue
    if ('QA' or 'Test' or 'Automation') not in title: continue
    print datePublished, title, '\n'+link

time.sleep(5)
"""
<a class="cl-link" href="https://globallogic.com.ua/position/macos-drivers-developer-for-avid-project-irc22902/">
<article class="content-listed position" itemscope="" itemtype="http://schema.org/JobPosting">
<header class="cl-hd">
<span class="cl-type" itemprop="additionalType">Position</span> / <time class="cl-date" datetime="2014-06-17" itemprop="datePublished" pubdate="">Июнь 17, 2014</time>
</header>
<section class="cl-bd">
<p class="cl-location" itemprop="jobLocation"><span class="icon-location"></span>Kyiv</p>
<h3 class="cl-title" itemprop="title">MacOS Drivers Developer for AVID project (IRC22902)</h3>
</section>
</article>
</a>
"""
