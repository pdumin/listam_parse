import selenium
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.common.exceptions import SessionNotCreatedException
import time
import json
import argparse

parser = argparse.ArgumentParser(description='Description of your program')
parser.add_argument('-l','--link', help='link to parse', required=False)
parser.add_argument('-n','--number', help='number of pages for parse', required=False)
parser.add_argument('-f','--filename', help='filename to save results', required=False)
args = vars(parser.parse_args())




def collect_page(
    page : selenium.webdriver.remote.webelement.WebElement
    ) -> dict:
    page_results = {}
    
    for ix, p in enumerate(page):
        try:
            href = p.get_property('href')
            id_ = href[href.rfind('/')+1:]
            
            try: 
                is_agency = True if p.find_element(By.CLASS_NAME, 'clabel').text == 'Агентство' else False
            except:
                is_agency = 'nd'
            address     = p.find_element(By.CLASS_NAME, 'at').text
            description = p.find_element(By.CLASS_NAME, 'l').text
            try: 
                price       = p.find_element(By.CLASS_NAME, 'p').text
            except Exception as e:
                price = 'nd'
            currency    = 'usd' if '$' in price else 'adm'    
            price       = ''.join([i for i in price if i.isdigit()])

            tmp_res = {
                                f'{id_}' : 
                                    {
                                        'is_agency' : is_agency,
                                        'address' : address,
                                        'description' : description,
                                        'currency' : currency,
                                        'price' : price
                                    }
                            }
            page_results.update(tmp_res)
    
        except Exception as e:
            pass

    return page_results


def iterate_over_pages(
    link: str, 
    number_of_pages: int,
    fname : str
    ) -> dict:
    """parse and save results to json file

    Args:
        link (str): link to start page
        number_of_pages (int): how many pages to parse
        fname (str): filename for results

    Returns:
        None
    """                    
    rent_dict = {}
    i = 0
    driver.get(link)
    page = driver.find_elements(By.CLASS_NAME, 'gl')[1].find_elements(By.TAG_NAME, 'a')
    for i in range(number_of_pages): 
        if i != 0:
            tmp_elem = driver.find_elements(By.PARTIAL_LINK_TEXT, 'Сл')[0]
            driver.execute_script('arguments[0].click();', tmp_elem)
            time.sleep(2)            
            page = driver.find_elements(By.CLASS_NAME, 'gl')[1].find_elements(By.TAG_NAME, 'a')
            new_results = collect_page(page)
            rent_dict.update(new_results)
        else: 
            new_results = collect_page(page)
            rent_dict.update(new_results)
        i += 1
    
    with open(f'{fname}', 'w') as f:
        f.write(json.dumps(rent_dict, ensure_ascii=False))


        
if __name__ == '__main__':
    try:
        driver.client_stop()
    except Exception as e:
        driver = webdriver.Safari()
    
    
    if args['link']:
        link = args['link']
    else:
        link = 'https://www.list.am/ru/category/56?pfreq=1&n=0&price1=&price2=&crc=-1&_a5=0&_a39=0&_a40=0&_a11_1=&_a11_2=&_a4=0&_a37=0&_a3_1=&_a3_2=&_a38=0&_a69=0'

    if args['number']:
        number_of_pages = int(args['number'])
    else:
        number_of_pages = 250

    if args['filename']:
        fname = args['filename']
    else:
        fname = 'results.json'

    iterate_over_pages(link, number_of_pages, fname)

    driver.stop_client()

