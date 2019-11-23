from bs4 import BeautifulSoup
import datetime
from random import randint
from random import shuffle
import requests
from time import sleep

def get_html(url):
    
    html_content = ''
    try:
        page = requests.get(url, headers={'User-Agent': 'Mozilla/5.0'})
        html_content = BeautifulSoup(page.content, "html.parser")
    except: 
        pass
    
    return html_content

def get_value(html, info_name):
    
    info_value = ''
    
    items = html.select('.product-attributes-list .attribute-label')
    for item in items:
        item_heading = item.get_text().strip()
        try:
            item_next = item.find_next().get_text().strip()
            if info_name == item_heading:
                info_value = item_next
                break
        except:
            pass
      
    return info_value 

def get_details(url):
    
    stamp = {}
    
    try:
        html = get_html(url)
    except:
        return stamp
    
    try:
        title = html.select('#single-product-name')[0].get_text().strip()
        stamp['title'] = title
    except: 
        stamp['title'] = None

    try:
        if html.select('.special-price'):
            price = html.select('.special-price')[0].get_text().strip()
        else:
            price = html.select('.regular-price .price')[0].get_text().strip()
        stamp['price'] = price.replace('£', '').strip()
    except: 
        stamp['price'] = None
        
    stamp['item_type'] = get_value(html, 'Type:')
    stamp['era'] = get_value(html, 'Era:')
    stamp['condition'] = get_value(html, 'Condition:')
    stamp['grade'] = get_value(html, 'Grade:')
    stamp['year'] = get_value(html, 'Year of Issue:')
        
    stamp['currency'] = 'GBP'

    # image_urls should be a list
    images = []                    
    try:
        image_items = html.select('a.mz-thumb')
        for image_item in image_items:
            img = image_item.get('href')
            if img not in images:
                images.append(img)
                
        if len(images) == 0:
            img = html.select('.MagicZoom')[0].get('href')
            images.append(img)
    except:
        pass
    
    stamp['image_urls'] = images 
    
    try:
        raw_text = html.select('.box-description')[0].get_text().strip()
        stamp['raw_text'] = raw_text.replace('\n', ' ')
    except:
        stamp['raw_text'] = None
        
    if stamp['raw_text'] == None and stamp['title'] != None:
        stamp['raw_text'] = stamp['title']
        
    # scrape date in format YYYY-MM-DD
    scrape_date = datetime.date.today().strftime('%Y-%m-%d')
    stamp['scrape_date'] = scrape_date

    stamp['url'] = url
    
    print(stamp)
    print('+++++++++++++')
    sleep(randint(25, 65))
           
    return stamp

def get_page_items(url):

    items = []
    next_url = ''

    try:
        html = get_html(url)
    except:
        return items, next_url

    try:
        for item in html.select('h3.product-name a'):
            item_link = item.get('href')
            if item_link not in items:
                items.append(item_link)
    except:
        pass
    
    try:
        next_url_elem = html.select('a.next')[0]
        if next_url_elem:
            next_url = next_url_elem.get('href')
    except:
        pass   
    
    shuffle(list(set(items)))
    
    return items, next_url

item_dict = {
'Commonwealth Stamps':'https://www.empirephilatelists.com/british-commonwealth-stamps',
'Stamp Collections':'https://www.empirephilatelists.com/stamp-collections',
'Rare Stamps':'https://www.empirephilatelists.com/rare-stamps',
'Errors and Varieties':'https://www.empirephilatelists.com/errors-and-varieties-stamps',
'GB Stamps':'https://www.empirephilatelists.com/great-britain-stamps',
'All World':'https://www.empirephilatelists.com/all-world-stamps',
'Sales':'https://www.empirephilatelists.com/sales'
    }
    
for key in item_dict:
    print(key + ': ' + item_dict[key])   

selection = input('Choose category: ')
            
category_url = item_dict[selection]
page_url = category_url
while(page_url):
    page_items, page_url = get_page_items(page_url)
    for page_item in page_items:
            stamp = get_details(page_item)
