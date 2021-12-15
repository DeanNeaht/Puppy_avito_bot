import pathlib
import time

import environs
from sqlalchemy import create_engine
from sqlalchemy.exc import IntegrityError
import bs4
import requests
from sqlalchemy.orm import Session

from models.models import dogs, Base
from apscheduler.schedulers.blocking import BlockingScheduler

sched = BlockingScheduler()

env = environs.Env()
env.read_env()


@sched.scheduled_job('interval', minutes=10)
def parse_and_send_to_bot():
    BASE_DIR = pathlib.Path(__file__).parent
    engine = create_engine('sqlite:///' + str(BASE_DIR / "models/dogs.sqlite3"))
    Base.metadata.create_all(engine)
    session = Session(bind=engine)
    dogs_list = items_validations()
    for dog in dogs_list:
        try:
            item = dogs(**dog)
            session.add(item)
            session.commit()
            requests.post(url=f"http://{env.str('IP')}:{env.str('PORT')}/dogs/", json=dog)
            time.sleep(5)
        except IntegrityError:
            session.rollback()
        except ConnectionError:
            pass
    session.close()


def items_validations():
    items = avito_parse()
    correct_items = []
    ignore = ['ркф', 'вязк', 'рфк', 'прод']
    for item in items:
        _ = 0
        for word in ignore:
            if word in item.get('description').lower():
                break
            if word in item.get('name').lower():
                break
            else:
                _ += 1
        if _ < len(ignore):
            continue
        else:
            if "\xa0₽" in item.get('price'):
                price = item.get('price').replace('\xa0₽', '')
                item["price"] = price[-5:]
            correct_items.append(item)
    return correct_items


def avito_parse():
    url = "https://www.avito.ru/kazan/sobaki"
    headers = {
        'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_11_6) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/53.0.2785.143 Safari/537.36',
        'Accept-Language': 'ru',
    }
    params = {
        "f": 'ASgCAgECAUXGmgwTeyJmcm9tIjowLCJ0byI6NTAwfQ',
        "q": 'щенки',
        "s": '104'
    }

    class_block = 'div.iva-item-root-Nj_hb.photo-slider-slider-_PvpN.iva-item-list-H_dpX.iva-item-redesign-nV4C4.iva-item-responsive-gIKjW.items-item-My3ih.items-listItem-Gd1jN.js-catalog-item-enum'
    i = 0
    while True:
        resp = requests.get(url=url, headers=headers, params=params)
        soup = bs4.BeautifulSoup(resp.text, 'lxml')
        container = soup.select(class_block)
        if len(container) != 0:
            break
        time.sleep(15)
    items = []
    for _ in container:
        try:
            item = {
                'item_id': _.get('id'),
                'item_url': "https://www.avito.ru" + _.select_one("a.iva-item-sliderLink-bJ9Pv").get('href'),
                'name': _.select_one("img.photo-slider-image-_Dc4I").get("alt"),
                'description': _.select_one(
                    "div.iva-item-text-_s_vh.iva-item-description-S2pXQ.text-text-LurtD.text-size-s-BxGpL").text,
                'price': _.select_one("span.price-text-E1Y7h.text-text-LurtD.text-size-s-BxGpL").text,
                'photo_url': _.select_one("img.photo-slider-image-_Dc4I").get("src")
            }
            items.append(item)
        except AttributeError:
            pass
    return items


sched.start()
