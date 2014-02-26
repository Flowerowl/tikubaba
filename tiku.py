#encoding:utf-8
from __future__ import unicode_literals

import os
import re

from bs4 import BeautifulSoup
import xlwt
from selenium import webdriver
from selenium.webdriver.common.keys import Keys

import response


URL = 'http://www.tikubaba.com/'
global gl_driver
gl_driver = webdriver.Firefox()
gl_driver.implicitly_wait(3)

def createxls(name, result):
    """创建excel"""
    wbk = xlwt.Workbook(encoding='utf-8', style_compression=0)
    sheet = wbk.add_sheet('sheet 1', cell_overwrite_ok=True)
    for i, row in enumerate(result):
        for j, col in enumerate(row.values()):
            sheet.write(i, j, col)
    wbk.save('%s.xls' % name)

def get_tiku():
    """获取首页所有课程名以及url"""
    linkdict = {}
    tables = BeautifulSoup(response.get_source(URL)).findAll('div', id='search_main')[0].findAll('table')
    for table in tables:
        name = table.findAll(attrs={'align': 'center'})
        try:
            if len(name) > 0:
                name = name[0].select('font')[0].text
            questions = table.findAll(attrs={'style': 'width:750px;'})[0].findAll('a')
            linkdict[name] = questions
        except:
            pass
    return linkdict

def get_types(url):
    """获取单章的题目类型"""
    soup = BeautifulSoup(response.get_source(url))
    types = [(i.text, i.get('href')) for i in soup.find('div', {'id': 'TypeIn'}).findAll('a')]
    return types

def get_pages(url):
    """获取当前页面的页数"""
    soup = BeautifulSoup(response.get_source(url))
    max_page = int(soup.find('div', {'id': 'Pages'}).findAll('a')[-1].get('href').split('.')[0].split('_')[1])
    return max_page

def get_details(url):
    """获取当前题目的解析, 并写入xls"""
    gl_driver.get(url)
    content = gl_driver.find_element_by_css_selector('div[style="border:1px dashed #929292;width:940px; padding:8px 10px 8px 10px;background-color:#fff; margin:0 0 0 1px;"]').text
    answer = gl_driver.find_element_by_id('jie').text
    comment = gl_driver.find_element_by_id('dian').text
    analysis = gl_driver.find_element_by_id('xi').text
    return [{'content': content,
            'answer': answer,
            'comment': comment,
            'analysis': analysis
            }]

def get_page_items(url):
    """获取当前页面的所有题目的解析页面地址"""
    soup = BeautifulSoup(response.get_source(url))
    items = [link.get('href') for link in soup.find('div', {'id': 'ProDiv'}).findAll('a') if link.get('href').startswith('http://www.tikubaba.com')]
    return items

def create_dir(name, title):
    """创建文件夹，根据课程名以及章节划分"""
    path = os.path.join(os.path.abspath('.'), unicode(name), unicode(title))
    if not os.path.exists(path):
        os.mkdir(path)
    return path

def main():
    linkdict = get_tiku() #获取首页所有课程列表
    for name, links in linkdict.items():
        for link in links:
            if link is not None:
                soup = BeautifulSoup('%s' % link).find('a')
                link = soup.get('href') #单个课程url
                title = soup.text #单个课程标题, 如: 第1章 集合与函数概念
                types = get_types(link) #[(选择题, http://www.tikubaba.com/class-69-1.html), ...]
                for tp in types:
                    type_page = tp[1].split('-')[0]+'-'+tp[1].split('-')[1]+'-%s.html'
                    page_num = get_pages(tp[1])
                    for page in range(page_num):
                        for url in get_page_items(type_page % str(page+1)):
                            #import pdb;pdb.set_trace()
                            result = get_details(url) #单道题目的答案
                            #path = create_dir(name, title)
                            #createxls(name+'-'+title+'-'+tp[0], result)

if __name__ == '__main__':
    main()
