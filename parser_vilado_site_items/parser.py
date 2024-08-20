import asyncio

import requests
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from webdriver_manager.chrome import ChromeDriverManager
from config.os_system import os_system
from service_apps import chrome_settings
from variables.bot_dialog import categories_url, items_url


class ViladoParser:
    def __init__(self):
        self.vilado_url = "http://vilado.ru/magazin-2"

    async def get_browser(self):
        try:
            service = Service(chrome_settings.chrome_driver_path)
            self.browser = webdriver.Chrome(service=service, options=chrome_settings.options)
        except:
            try:
                service = Service(chrome_settings.chrome_driver_path)
                self.browser = webdriver.Chrome(service=service, options=chrome_settings.options)
            except Exception as ex:
                print(f"ERROR get_browser", ex)
            pass
        pass

    async def get_categories_items(self):
        self.browser.get(self.vilado_url)
        categories_xpath = "/html/body/div[1]/section/aside/nav/ul/li/a"
        categories = self.browser.find_elements(By.XPATH, categories_xpath)
        categories = [{"name": i.text, "url": i.get_attribute('href')} for i in categories]
        for category in range(len(categories)):
            categories[category] = await self.get_items_from_category(categories[category])
        pass


    async def get_items_from_category(self, category:dict):
        self.browser.get(category['url'])
        items_xpath = "//form[@method='post']"
        items = self.browser.find_elements(By.XPATH, items_xpath)
        category['items'] = []

        category_id, response, status_code = await self.post_database(model='categories', object_dict={"name": category['name']})
        pass

        n = 1
        for item in items:
            image_url_xpath = "div[@class='product-top']/div[@class='product-image']/a/img"
            site_card_item_path = "div[@class='product-top']/div[@class='product-image']/a"
            name_xpath = "div[@class='product-top']/div[@class='product-name']/a"
            article_xpath = "div[@class='product-top']/div[@class='product-article']"
            manufacturer_xpath = "div[@class='product-top']/table[@class='shop2-product-options']/tbody/tr[@class='even']"
            size_xpath = "div[@class='product-top']/table[@class='shop2-product-options']/tbody/tr[@class='odd type-select']"
            composition_xpath = "div[@class='product-top']/table[@class='shop2-product-options']/tbody/tr[@class='even type-select']"
            price_xpath = "div[@class='product-bot']/div[@class='product-price']/div[@class='price-current']"

            img_url = await self.get_element(instance=item, xpath=image_url_xpath, get_attribute='src')
            site_card_item = await self.get_element(instance=item, xpath=site_card_item_path, get_attribute='href')
            name = await self.get_element(instance=item, xpath=name_xpath, text=True)
            article = await self.get_element(instance=item, xpath=article_xpath, text=True, split=':')
            manufacturer = await self.get_element(instance=item, xpath=manufacturer_xpath, text=True, split=' ')
            size = await self.get_element(instance=item, xpath=size_xpath, text=True, split=' ')
            composition = await self.get_element(instance=item, xpath=composition_xpath, text=True, split=' ')
            price = await self.get_element(instance=item, xpath=price_xpath, text=True)

            item_json = {
                "img_url":  img_url,
                "site_card_item": site_card_item,
                "name": name,
                "article": article,
                "manufacturer": manufacturer,
                "size": size,
                "composition": composition,
                "price": price,
                "category": category_id
            }

            id, response, status_code = await self.post_database(model='item', object_dict=item_json)
            if status_code > 300:
                print("STATUS CODE", status_code, response.json())
            else:
                category['items'].append(item_json)

                print(
                    "number", n, "\n",
                    "img_url", img_url, "\n",
                    "site_card_item", site_card_item, "\n",
                    "name", name, "\n",
                    "article", article, "\n",
                    "manufacturer", manufacturer, "\n",
                    "size", size, "\n",
                    "composition", composition, "\n",
                    "price", price, "\n"
                )
                n += 1
        return category

    async def get_element(self, instance, xpath, **kwargs) -> str|None:
        try:
            if kwargs.get('get_attribute'):
                element = instance.find_element(By.XPATH, xpath).get_attribute(kwargs['get_attribute'])
            elif kwargs.get('text'):
                element = instance.find_element(By.XPATH, xpath).text
            else:
                element = instance.find_element(By.XPATH, xpath)
            return element.split(kwargs['split'], 1)[1].strip() if kwargs.get('split') else element.strip()
        except:
            return None

    async def get_items_from_Vilado(self):
        await self.get_browser()
        await self.get_categories_items()
        self.browser.quit()

    @classmethod
    async def post_database(cls, model:str, object_dict:dict) -> [int | str]:
        match model:
            case "categories":
                url = categories_url
                response = requests.post(url, object_dict)
            case "item":
                url = items_url
                response = requests.post(url, object_dict)
            case _:
                return None, None, 500
        query_param = await cls.repack_dict_to_query_params(object_dict)
        id = requests.get(url + query_param)
        id = id.json()
        if type(id) is dict and not id.get('error'):
            return id['queryset']['id'], response.json(), response.status_code
        return None, response, response.status_code

    @classmethod
    async def repack_dict_to_query_params(cls, query_params) -> str:
        url_query_param = "?"
        for key, value in query_params.items():
            url_query_param += f"{key}={value}&"
        return url_query_param[:-1]

if __name__ == "__main__":
    p = ViladoParser()
    asyncio.run(p.get_browser())
    pass