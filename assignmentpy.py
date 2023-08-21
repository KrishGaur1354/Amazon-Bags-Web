import requests
from bs4 import BeautifulSoup
import csv
import time



def scrape_product_listing(url, pages):
    headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.3"}
    products = []

    for page in range(1, pages+1):
        print(f'Scraping page {page}...')
        try:
            req = requests.get(url + str(page), headers=headers)
            req.raise_for_status()
        except requests.exceptions.RequestException as e:
            print(f'Error requesting page {page}: {e}')
            continue

        soup = BeautifulSoup(req.content, 'html.parser')

        for product in soup.find_all('div', {'class': 'sg-col-inner'}):
            try:
                name = product.find('span', {'class': 'a-size-base-plus'}).text.strip()
                url = 'https://www.amazon.in' + product.find('a', {'class': 'a-link-normal'})['href']
                price = product.find('span', {'class': 'a-offscreen'}).text.strip()
                rating = product.find('span', {'class': 'a-icon-alt'}).text.strip()
                reviews = product.find('span', {'class': 'a-size-base'}).text.strip()

                products.append([name, url, price, rating, reviews])
            except AttributeError:
                print('Error finding product information')
                continue

        time.sleep(5)

    return products


def scrape_product_details(products):
    headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.3"}
    details = []

    for i, product in enumerate(products, 1):
        print(f'Scraping product {i}/{len(products)}...')
        try:
            req = requests.get(product[1], headers=headers)
            req.raise_for_status()
        except requests.exceptions.RequestException as e:
            print(f'Error requesting product {i}: {e}')
            continue

        soup = BeautifulSoup(req.content, 'html.parser')

        try:
            description = soup.find('div', {'id': 'productDescription'}).text.strip()
            asin = soup.find('div', {'id': 'detailBullets_feature_div'}).find('span', text='ASIN').find_next('span').text.strip()
            manufacturer = soup.find('div', {'id': 'detailBullets_feature_div'}).find('span', text='Manufacturer').find_next('span').text.strip()

            details.append([product[0], product[1], description, asin, manufacturer])
        except AttributeError:
            print('Error finding product details')
            continue

        time.sleep(5)

    return details


url = "https://www.amazon.in/s?k=bags&crid=2M096C61O4MLT&qid=1653308124&sprefix=ba%2Caps%2C283&ref=sr_pg_"
products = scrape_product_listing(url, 5)

with open('products.csv', 'w', newline='', encoding='utf-8') as f:
    writer = csv.writer(f)
    writer.writerow(['Name', 'URL', 'Price', 'Rating', 'Number of Reviews'])
    writer.writerows(products)

details = scrape_product_details(products)

with open('product_details.csv', 'w', newline='', encoding='utf-8') as f:
    writer = csv.writer(f)
    writer.writerow(['Name', 'URL', 'Description', 'ASIN', 'Manufacturer'])
    writer.writerows(details)
