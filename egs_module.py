from epicstore_api import EpicGamesStoreAPI
from datetime import datetime, timezone
import requests, os
import sql_module, tg_module

if os.name != 'nt':
    app_path_divider = '/'
else:
    app_path_divider = '\\'
root_dir = os.path.dirname(__file__) + app_path_divider

api = EpicGamesStoreAPI()

def date_format(date):
    date = datetime.fromisoformat(date[:-1]).astimezone(timezone.utc)
    date = f"{date.strftime('%Y-%m-%d %H:%M:%S')} UTC"
    return date

def check_egs():
    status = api.get_epic_store_status()['status']['description']
    return status

def check_games_data():
    free_games = api.get_free_games(allow_countries='Poland')['data']['Catalog']['searchStore']['elements']
    for game in free_games:
        if game['promotions']:
            if game['promotions']['promotionalOffers']:
                if game['promotions']['promotionalOffers'][0]['promotionalOffers'][0]['discountSetting']['discountPercentage'] == 0:
                    current_random_title = game['title']
                    break
    if sql_module.check_games_data(current_random_title):
        return True
    else:
        return False

def game_data_update():
    free_games = api.get_free_games(allow_countries='Poland')['data']['Catalog']['searchStore']['elements']
    tags = api.fetch_catalog_tags()['data']['Catalog']['tags']['elements']
    sql_module.clean_games_data()
    image_counter = 1
    for game in free_games:
        if game['promotions']:
            if game['promotions']['promotionalOffers']:
                if game['promotions']['promotionalOffers'][0]['promotionalOffers'][0]['discountSetting']['discountPercentage'] == 0:
                    image_dir_path = root_dir + 'pic_current' + app_path_divider
                    title = game['title']
                    tag_list = []
                    for gametag in game['tags']:
                        for shoptag in tags:
                            if shoptag['id'] == gametag['id']:
                                tag_list.append(shoptag['name'])
                    description = game['description']
                    for game_image in game['keyImages']:
                        if game_image['type'] == 'OfferImageTall':
                            image = requests.get(game_image['url']).content
                            image_path = f"{image_dir_path}{image_counter}.jpg"
                            with open(image_path, 'wb') as handler:
                                handler.write(image)
                            image_counter += 1
                    end_offer_date = game['promotions']['promotionalOffers'][0]['promotionalOffers'][0]['endDate']
                    end_offer_date = date_format(end_offer_date)
                    for page in game['catalogNs']['mappings']:
                        if page['pageType'] == 'productHome':
                            page_path = page['pageSlug']
                    sql_module.update_current_game_data(title,description,image_path,end_offer_date,page_path)
                    sql_module.update_game_tags(title,tag_list)
            if game['promotions']['upcomingPromotionalOffers']:
                if game['promotions']['upcomingPromotionalOffers'][0]['promotionalOffers'][0]['discountSetting']['discountPercentage'] == 0:
                    image_dir_path = root_dir + 'pic_upcoming' + app_path_divider
                    title = game['title']
                    tag_list = []
                    for gametag in game['tags']:
                        for shoptag in tags:
                            if shoptag['id'] == gametag['id']:
                                tag_list.append(shoptag['name'])
                    description = game['description']
                    for game_image in game['keyImages']:
                        if game_image['type'] == 'OfferImageTall':
                            image = requests.get(game_image['url']).content
                            image_path = f'{image_dir_path}{image_counter}.jpg'
                            with open(image_path, 'wb') as handler:
                                handler.write(image)
                            image_counter += 1
                    start_offer_date = game['promotions']['upcomingPromotionalOffers'][0]['promotionalOffers'][0]['startDate']
                    start_offer_date = date_format(start_offer_date)
                    end_offer_date = game['promotions']['upcomingPromotionalOffers'][0]['promotionalOffers'][0]['endDate']
                    end_offer_date = date_format(end_offer_date)
                    for page in game['catalogNs']['mappings']:
                        if page['pageType'] == 'productHome':
                            page_path = page['pageSlug']
                    sql_module.update_upcoming_game_data(title,description,image_path,start_offer_date,end_offer_date,page_path)
                    sql_module.update_game_tags(title,tag_list)