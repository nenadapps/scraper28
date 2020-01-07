#empire_phil
from bs4 import BeautifulSoup
import datetime
from random import randint
from random import shuffle
import requests
from time import sleep
'''
from fake_useragent import UserAgent
import os
import sqlite3
import shutil
from stem import Signal
from stem.control import Controller
import socket
import socks

controller = Controller.from_port(port=9051)
controller.authenticate()

def connectTor():
    socks.setdefaultproxy(socks.PROXY_TYPE_SOCKS5 , "127.0.0.1", 9050)
    socket.socket = socks.socksocket

def renew_tor():
    controller.signal(Signal.NEWNYM)
    
UA = UserAgent(fallback='Mozilla/5.0 (Windows NT 6.1) AppleWebKit/537.2 (KHTML, like Gecko) Chrome/22.0.1216.0 Safari/537.2')
hdr = {'User-Agent': UA.random}
'''
hdr = {'User-Agent': 'Mozilla/5.0'}

def get_html(url):
    
    html_content = ''
    try:
        page = requests.get(url, headers=hdr)
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
        stamp['raw_text'] = raw_text.replace('\n', ' ').replace('\xa0',' ').replace('"',"'")
    except:
        stamp['raw_text'] = None
        
    if stamp['raw_text'] == None and stamp['title'] != None:
        stamp['raw_text'] = stamp['title'].replace('"',"'")
        
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
'''
def file_names(stamp):
    file_name = []
    rand_string = "RAND_"+str(randint(0,100000000))
    file_name = [rand_string+"-" + str(i) + ".png" for i in range(len(stamp['image_urls']))]
    print (file_name)
    return(file_name)

def query_for_previous(stamp):
    # CHECKING IF Stamp IN DB
    os.chdir("/Volumes/Stamps/")
    conn1 = sqlite3.connect('Reference_data.db')
    c = conn1.cursor()
    col_nm = 'url'
    col_nm2 = 'raw_text'
    unique = stamp['url']
    unique2 = stamp['raw_text']
    c.execute('SELECT * FROM empire_phil WHERE {cn} == "{un}" AND {cn2} == "{un2}"'.format(cn=col_nm, cn2=col_nm2, un=unique, un2=unique2))
    all_rows = c.fetchall()
    conn1.close()
    price_update=[]
    price_update.append((stamp['url'],
    stamp['raw_text'],
    stamp['scrape_date'], 
    stamp['price'], 
    stamp['currency']))
    
    if len(all_rows) > 0:
        print ("This is in the database already")
        conn1 = sqlite3.connect('Reference_data.db')
        c = conn1.cursor()
        c.executemany("""INSERT INTO price_list (url, raw_text, scrape_date, price, currency) VALUES(?,?,?,?,?)""", price_update)
        try:
            conn1.commit()
            conn1.close()
        except:
            conn1.commit()
            conn1.close()
        print (" ")
        sleep(randint(10,45))
        next_step = 'continue'
    else:
        os.chdir("/Volumes/Stamps/")
        conn2 = sqlite3.connect('Reference_data.db')
        c2 = conn2.cursor()
        c2.executemany("""INSERT INTO price_list (url, raw_text, scrape_date, price, currency) VALUES(?,?,?,?,?)""", price_update)
        try:
            conn2.commit()
            conn2.close()
        except:
            conn2.commit()
            conn2.close()
        next_step = 'pass'
    print("Price Updated")
    return(next_step)

def db_update_image_download(stamp): 
    req = requests.Session()
    directory = "/Volumes/Stamps/stamps/empire_phil/" + str(datetime.datetime.today().strftime('%Y-%m-%d')) +"/"
    image_paths = []
    names = file_names(stamp)
    if not os.path.exists(directory):
        os.makedirs(directory)
    os.chdir(directory)
    image_paths = [directory + names[i] for i in range(len(names))]
    for item in range(len(names)):
        print (stamp['image_urls'][item])
        try:
            imgRequest1=req.get(stamp['image_urls'][item],headers=hdr, timeout=120, stream=True)
        except:
            print ("waiting...")
            sleep(randint(3000,6000))
            print ("...")
            imgRequest1=req.get(stamp['image_urls'][item], headers=hdr, timeout=120, stream=True)
        if imgRequest1.status_code==200:
            with open(names[item],'wb') as localFile:
                imgRequest1.raw.decode_content = True
                shutil.copyfileobj(imgRequest1.raw, localFile)
                sleep(randint(18,30))
    stamp['image_paths']=", ".join(image_paths)
    database_update =[]
    # PUTTING NEW STAMPS IN DB
    database_update.append((
        stamp['url'],
        stamp['raw_text'],
        stamp['title'],
        stamp['year'],
        stamp['condition'],
        stamp['grade'],
        stamp['item_type'],
        stamp['era'],
        stamp['scrape_date'],
        stamp['image_paths']))
    os.chdir("/Volumes/Stamps/")
    conn = sqlite3.connect('Reference_data.db')
    conn.text_factory = str
    cur = conn.cursor()
    cur.executemany("""INSERT INTO empire_phil ('url','raw_text', 'title','year',
    'condition','grade','item_type','era','scrape_date','image_paths') 
    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)""", database_update)
    try:
        conn.commit()
        conn.close()
    except:
        conn.commit()
        conn.close()
    print ("all updated")
    print ("++++++++++++")
    print (" ")
    sleep(randint(45,140)) 

connectTor()
count = 0
'''

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
        '''
        count += 1
        if count > randint(100, 256):
            print('Sleeping...')
            sleep(randint(600, 4000))
            hdr['User-Agent'] = UA.random
            renew_tor()
            connectTor()
            count = 0
        else:
            pass'''
        stamp = get_details(page_item)
        '''if stamp['price']==None or stamp['price']=='':
            sleep(randint(500,700))
            continue
        next_step = query_for_previous(stamp)
        if next_step == 'continue':
            print('Only updating price')
            continue
        elif next_step == 'pass':
            print('Inserting the item')
            pass
        else:
            break
        db_update_image_download(stamp)
        count += 1'''
print('Scrape Complete')