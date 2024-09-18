from epicstore_api import EpicGamesStoreAPI, OfferData
import sys
from datetime import datetime, timezone
import json

emoji_bookmark = u'\U0001F516'
emoji_gamepad = u'\U0001F3AE'
emoji_scroll = u'\U0001F4DC'
emoji_hourglass = u'\U0000231B'

api = EpicGamesStoreAPI()

def date_format(date):
    date = datetime.fromisoformat(date[:-1]).astimezone(timezone.utc)
    local_timezone = datetime.now().astimezone().tzname()
    date = f'{date.strftime('%Y-%m-%d %H:%M:%S')} {local_timezone}'
    return date

def check_egs():
    status = api.get_epic_store_status()['status']['description']
    return status

def get_current_games_data():
    free_games = api.get_free_games(allow_countries='Poland')['data']['Catalog']['searchStore']['elements']
    tags = api.fetch_catalog_tags()['data']['Catalog']['tags']['elements']
    games_data = '\ncurrent free titles:\n\n'
    games_pic_links = []
    for game in free_games:
        if game['promotions']:
            if game['promotions']['promotionalOffers']:
                for game_image in game['keyImages']:
                    if game_image['type'] == 'Thumbnail':
                        games_pic_links.append(game_image['url'])
                games_data += f'{emoji_gamepad} {game['title']} {emoji_gamepad}\n'
                games_data += 'tags:\n'
                for gametag in game['tags']:
                    for shoptag in tags:
                        if shoptag['id'] == gametag['id']:
                            games_data += f'  {emoji_bookmark} {shoptag['name']}\n'
                games_data += f' {emoji_scroll} {game['description']}\n'
                offer_date = game['promotions']['promotionalOffers'][0]['promotionalOffers'][0]['endDate']
                games_data += f'{emoji_hourglass} offer valid until:\n'
                games_data += f'  {date_format(offer_date)}\n'
                games_data += '\n'
    return games_data, games_pic_links

def get_upcoming_games_data():
    free_games = api.get_free_games(allow_countries='Poland')['data']['Catalog']['searchStore']['elements']
    tags = api.fetch_catalog_tags()['data']['Catalog']['tags']['elements']
    games_data = '\nupcoming free titles:\n\n'
    games_pic_links = []
    for game in free_games:
        if game['promotions']:
            if game['promotions']['upcomingPromotionalOffers']:
                if game['promotions']['upcomingPromotionalOffers'][0]['promotionalOffers'][0]['discountSetting']['discountPercentage'] == 0:
                    for game_image in game['keyImages']:
                        if game_image['type'] == 'Thumbnail':
                            games_pic_links.append(game_image['url'])
                    games_data += f'{emoji_gamepad} {game['title']} {emoji_gamepad}\n'
                    games_data += 'tags:\n'
                    for gametag in game['tags']:
                        for shoptag in tags:
                            if shoptag['id'] == gametag['id']:
                                games_data += f'  {emoji_bookmark} {shoptag['name']}\n'
                    games_data += f' {emoji_scroll} {game['description']}\n'
                    start_offer_date = game['promotions']['upcomingPromotionalOffers'][0]['promotionalOffers'][0]['startDate']
                    end_offer_date = game['promotions']['upcomingPromotionalOffers'][0]['promotionalOffers'][0]['endDate']
                    games_data += f'{emoji_hourglass} offer valid since:\n'
                    games_data += f'  {date_format(start_offer_date)}\n'
                    games_data += f'{emoji_hourglass} offer valid until:\n'
                    games_data += f'  {date_format(end_offer_date)}\n'
                    games_data += '\n'
    return games_data, games_pic_links