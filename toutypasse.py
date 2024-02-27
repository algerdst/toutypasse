import json

from selenium import webdriver
from selenium.webdriver.common.by import By
import requests
from bs4 import BeautifulSoup
import os
import csv
from datetime import datetime
import sys




headers = {
    'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/118.0.0.0 YaBrowser/23.11.0.0 Safari/537.36'
}

url = 'https://www.toutypasse.ch/'
response = requests.get(url, headers=headers)  # получаю главную страницу
soup = BeautifulSoup(response.text, 'lxml')
categories_links = soup.find_all('li', class_='index_title')  # ищу блоки с названиями категорий
links_count = 0 #подсчет собранных ссылок
for category in categories_links:  # прохожу по блокам с названиями
    category_link = category.find('a')['href']  # получаю ссылку на категорию
    response = requests.get(category_link, headers=headers)
    soup = BeautifulSoup(response.text, 'lxml')
    try:
        pages = int(soup.find('div', class_='pagination').find_all('a')[-2].text)  # узнаю количество страниц в категории
    except:
        pages=1 # если блок pages не найден, то существует только одна страница
      # открываю txt в файл в который запишу все ссылки
    for page in range(1, pages):
        if page == 1:
            link = category_link
        else:
            link = f"{category_link}?page={page}"
        response = requests.get(link, headers=headers)
        soup = BeautifulSoup(response.text, 'lxml')
        blocks = soup.find_all('h2', class_='serow_title')
        for block in blocks:
            link = block.find('a')['href']
            response = requests.get(link, headers=headers)
            soup = BeautifulSoup(response.text, 'lxml')
            try:  # если в объявке есть кнопка для просмотра телефона, сохраняю ссылку на объявку, если нет, то пропущу
                button = soup.find(id='phone_btn')
                if button:
                    with open('links.txt', 'a', encoding='utf-8') as file:
                        file.write(link + '\n')
                    links_count += 1
                    print(f"Найдено ссылок {links_count}")
            except:
                continue
print(f"Всего найдено ссылок {links_count}")

with open('phones.json', 'r', encoding='utf-8') as file: #открываю файл с сохраненными телефонами и присваиваю в переменную phones
    phones=json.load(file)

print('CБОР НОМЕРОВ')
print(5*"\n")
with webdriver.Chrome() as browser: # cоздаю экземпляр вебдрайвера
    with open('links.txt', 'r', encoding='utf-8') as file:
        for link in file:
            link=link.replace('\n','')
            browser.get(link)
            try:
                cookie_buttons = browser.find_element(By.CLASS_NAME, 'user-menu1').find_elements(By.TAG_NAME, 'button')
                for btn in cookie_buttons:
                    if btn.text == 'Accepter':
                        btn.click()
            except:
                print()
            try:
                browser.find_element(By.ID, 'phone_btn').click()
                phone=browser.find_element(By.ID, 'phone_number').text
                print(f"{phone}")
            except:
                continue
            try:
                name=browser.find_element(By.CLASS_NAME, 'uiname').text.split('\n')[0]
            except:
                name='-'
            try:
                location=browser.find_elements(By.CLASS_NAME, 'feature_value')[1].text
            except:
                location='-'
            if phone not in phones:
                phones[phone]=f"{name} {location}"
                with open('phones.json', 'w',
                          encoding='utf-8') as file:  # открываю файл с сохраненными телефонами и присваиваю в переменную phones
                    json.dump(phones, file, indent=4, ensure_ascii=False)
                with open('phones.json', 'r',
                          encoding='utf-8') as file:  # открываю файл с сохраненными телефонами и присваиваю в переменную phones
                    phones = json.load(file)
                with open('result.csv', 'a', newline='', encoding='utf-8-sig') as file:
                    writer=csv.writer(file, delimiter=';')
                    writer.writerow([phone, name, location])
            else:
                continue
os.remove('links.txt')

