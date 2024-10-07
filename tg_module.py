from telethon import TelegramClient, events
from telethon.tl.types import PeerUser, PeerChat, PeerChannel
import preconfig, egs_module, sql_module

emoji_bookmark = u'\U0001F516'
emoji_gamepad = u'\U0001F3AE'
emoji_scroll = u'\U0001F4DC'
emoji_hourglass = u'\U0000231B'
emoji_link = u'\U0001F517'

def generate_message_current():
    try:
        game_data_list, image_list = sql_module.get_current_game_data()
        message_text = "\ncurrent free titles:\n\n"
        for game_data in game_data_list:
            message_text += f"{emoji_gamepad} {game_data['Title']} {emoji_gamepad}\n"
            message_text += 'tags:\n'
            for game_tag in game_data['Tag']:
                message_text += f"  {emoji_bookmark} {game_tag}\n"
            message_text += f" {emoji_scroll} {game_data['Description']}\n"
            message_text += f" {emoji_hourglass} offer valid until:\n"
            message_text += f"  {game_data['EndDate']}\n"
            message_text += f" {emoji_link} https://store.epicgames.com/en-US/p/{game_data['Page']}\n\n"
        return image_list, message_text
    except Exception as exception:
        print(f"[ERROR] {exception}")
        message_text = 'Something went wrong, please check store status with /egs_status@epic_announcement_bot command'
        return None, message_text

def generate_message_upcoming():
    try:
        game_data_list, image_list = sql_module.get_upcoming_game_data()
        message_text = "\nupcoming free titles:\n\n"
        for game_data in game_data_list:
            message_text += f"{emoji_gamepad} {game_data['Title']} {emoji_gamepad}\n"
            message_text += "tags:\n"
            for game_tag in game_data['Tag']:
                message_text += f"  {emoji_bookmark} {game_tag}\n"
            message_text += f" {emoji_scroll} {game_data['Description']}\n"
            message_text += f"{emoji_hourglass} offer valid since:\n"
            message_text += f"  {game_data['StartDate']}\n"
            message_text += f"{emoji_hourglass} offer valid until:\n"
            message_text += f"  {game_data['EndDate']}\n"
            message_text += f" {emoji_link} https://store.epicgames.com/en-US/p/{game_data['Page']}\n\n"
        return image_list, message_text
    except Exception as exception:
        print(f"[ERROR] {exception}")
        message_text = 'Something went wrong, please check store status with /egs_status@epic_announcement_bot command'
        return None, message_text


api_id, api_hash, bot_token = preconfig.preconfigure()
client = TelegramClient('handle_session', api_id, api_hash).start(bot_token=bot_token)

def tg_handler():
    client.start()

@client.on(events.NewMessage(pattern='^/start$'))
async def handle_start_command(event):
    chat_id = event.message.peer_id
    if isinstance(chat_id, (PeerUser)):
        await client.send_message(chat_id, 'Hello friend, my name is Epic Bot. I monitor EGS free games info and share it. Please use /help command to see what I can do!')

@client.on(events.NewMessage(pattern='^/help$'))
async def handle_start_command(event):
    chat_id = event.message.peer_id
    if isinstance(chat_id, (PeerUser, PeerChat, PeerChannel)):
        await client.send_message(chat_id, '''Here is what I can do:
/subscribe@epic_announcement_bot - start news subscription
/unsubscribe@epic_announcement_bot - cansel news subscription
/egs_status@epic_announcement_bot - check EGS services status
/current_games@epic_announcement_bot - show current free games in EGS
/upcoming_games@epic_announcement_bot - show upcoming free games in EGS
\nAfter subscribing you will recieve free game offer updates on day it will be made in EGS.''')

@client.on(events.NewMessage(pattern='^/subscribe@epic_announcement_bot$'))
async def handle_start_command(event):
    chat_id = event.message.peer_id
    if isinstance(chat_id, (PeerUser, PeerChat, PeerChannel)):
        chat_id = await client.get_entity(chat_id)
        chat_id_int = chat_id.id
        if not sql_module.check_subscriber(chat_id_int):
            sql_module.add_subscriber(chat_id_int)
            print(f"[INFO] subscribed chat: {chat_id_int}")
            await client.send_message(chat_id, 'Now I will start sharing EGS free games data with you!')
        else:
            await client.send_message(chat_id, 'Already subscribed!')

@client.on(events.NewMessage(pattern='^/unsubscribe@epic_announcement_bot$'))
async def handle_start_command(event):
    chat_id = event.message.peer_id
    if isinstance(chat_id, (PeerUser, PeerChat, PeerChannel)):
        chat_id = await client.get_entity(chat_id)
        chat_id_int = chat_id.id
        if sql_module.check_subscriber(chat_id_int):
            sql_module.delete_subscriber(chat_id_int)
            print(f"[INFO] unsubscribed chat: {chat_id_int}")
            await client.send_message(chat_id, 'Got it, no more information about free games needed. See ya!')
        else:
            await client.send_message(chat_id, 'Not subscribed yet!')

@client.on(events.NewMessage(pattern='^/egs_status@epic_announcement_bot$'))
async def handle_start_command(event):
    chat_id = event.message.peer_id
    status = egs_module.check_egs()
    await client.send_message(chat_id, f"EGS status: {status}")

@client.on(events.NewMessage(pattern='^/current_games@epic_announcement_bot$'))
async def handle_start_command(event):
    chat_id = event.message.peer_id
    if isinstance(chat_id, (PeerUser, PeerChat, PeerChannel)):
        image_list, message_text = generate_message_current()
        if image_list != []:
            await client.send_file(chat_id, image_list)
            await client.send_message(chat_id, message_text, link_preview=False)
        else:
            await client.send_message(chat_id, 'Something went wrong, please check store status with /egs_status@epic_announcement_bot command')

@client.on(events.NewMessage(pattern='^/upcoming_games@epic_announcement_bot$'))
async def handle_start_command(event):
    chat_id = event.message.peer_id
    if isinstance(chat_id, (PeerUser, PeerChat, PeerChannel)):
        image_list, message_text = generate_message_upcoming()
        if image_list != []:
            await client.send_file(chat_id, image_list)
            await client.send_message(chat_id, message_text, link_preview=False)
        else:
            await client.send_message(chat_id, 'Something went wrong, please check store status with /egs_status@epic_announcement_bot command')

async def notify_subscribers():
    image_list, message_text = generate_message_current()
    if image_list != []:
        subscribers_list = sql_module.get_all_subscribers()
        for subscriber in subscribers_list:
            await client.send_file(subscriber, image_list, caption=message_text)

# admin handlers

def generate_message_admin(admins_list, subscribers_list):
    message_text = f"subscribers number: {len(subscribers_list)}"
    if len(subscribers_list) > 0:
        message_text = message_text + '\nsubscribers list:'
        for subscriber in subscribers_list:
            message_text = message_text + f"\n  {subscriber}"
    message_text = message_text + f"\n\nadmins number: {len(admins_list)}"
    if len(admins_list) > 0:
        message_text = message_text + '\nadmins list:'
        for admin in admins_list:
            message_text = message_text + f"\n  {admin}"
    return message_text

@client.on(events.NewMessage(pattern='^/admin_get_data@epic_announcement_bot$'))
async def handle_start_command(event):
    chat_id = event.message.peer_id
    if isinstance(chat_id, (PeerUser)):
        admins_list = sql_module.get_all_admins()        
        chat_id = await client.get_entity(chat_id)
        chat_id_int = chat_id.id
        if chat_id_int in admins_list:
            subscribers_list = sql_module.get_all_subscribers()
            message_text = generate_message_admin(admins_list, subscribers_list)
            await client.send_message(chat_id, message_text)

@client.on(events.NewMessage(pattern='^/admin_force_refresh@epic_announcement_bot$'))
async def handle_start_command(event):
    chat_id = event.message.peer_id
    if isinstance(chat_id, (PeerUser)):
        admins_list = sql_module.get_all_admins()    
        chat_id = await client.get_entity(chat_id)
        chat_id_int = chat_id.id
        if chat_id_int in admins_list:
            egs_module.game_data_update()
            await client.send_message(chat_id, 'database was updated')