from telethon import TelegramClient, events
from telethon.tl.types import PeerUser, PeerChat, PeerChannel, DocumentAttributeVideo
import os
import yaml
import asyncio
import egs_module, sql_module

sql_module.set_db()

if os.name != 'nt':
    print("[INFO] non-Windows paths detected")
    app_path_divider = '/'
else:
    print("[INFO] Windows paths detected")
    app_path_divider = '\\'

for directory in ['pic_current', 'pic_upcoming']:
    if not os.path.exists(os.path.dirname(__file__) + app_path_divider + directory):
        os.makedirs(os.path.dirname(__file__) + app_path_divider + directory)

def read_env_from_file():
    try:
        app_variable_file = os.path.dirname(__file__) + app_path_divider + 'var.yaml'
        with open(app_variable_file) as env_file:
            env_data = yaml.safe_load(env_file)
            return env_data
    except Exception as exception:
        print(f"[ERROR]\ncannot find variables\nerror message: {exception}")
        return None

def set_env(env):
    if os.getenv(env):
        print (f"[INFO] found {env} in system environment")
        return os.environ[env]
    else:
        return app_var_files[env]

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
            message_text += f"  {game_data['EndDate']}\n\n"
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
            message_text += f"  {game_data['EndDate']}\n\n"
        return image_list, message_text
    except Exception as exception:
        print(f"[ERROR] {exception}")
        message_text = 'Something went wrong, please check store status with /egs_status@epic_announcement_bot command'
        return None, message_text

emoji_bookmark = u'\U0001F516'
emoji_gamepad = u'\U0001F3AE'
emoji_scroll = u'\U0001F4DC'
emoji_hourglass = u'\U0000231B'

app_var_files = read_env_from_file()
api_id = set_env('TG_API_ID')
api_hash = set_env('TG_API_HASH')
bot_token = set_env('TG_BOT_TOKEN')
client = TelegramClient('handle_session', api_id, api_hash).start(bot_token=bot_token)

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
            await client.send_file(chat_id, image_list, caption=message_text)
        else:
            await client.send_message(chat_id, 'Something went wrong, please check store status with /egs_status@epic_announcement_bot command')

@client.on(events.NewMessage(pattern='^/upcoming_games@epic_announcement_bot$'))
async def handle_start_command(event):
    chat_id = event.message.peer_id
    if isinstance(chat_id, (PeerUser, PeerChat, PeerChannel)):
        image_list, message_text = generate_message_upcoming()
        if image_list != []:
            await client.send_file(chat_id, image_list, caption=message_text)
        else:
            await client.send_message(chat_id, 'Something went wrong, please check store status with /egs_status@epic_announcement_bot command')

async def notify_subscribers():
    image_list, message_text = generate_message_current()
    if image_list != []:
        subscribers_list = sql_module.get_all_subscribers()
        for subscriber in subscribers_list:
            await client.send_file(subscriber, image_list, caption=message_text)

async def scheduled_egs_check():
    while True:
        if await asyncio.to_thread(egs_module.check_games_data):
            print('[INFO] data is being updated')
            await asyncio.to_thread(egs_module.game_data_update)
            print('[INFO] data was updated')
            await notify_subscribers()
            print('[INFO] subscribers were notified')
        await asyncio.sleep(86400)

try:
    loop = asyncio.get_event_loop()
    client.start()
    loop.create_task(scheduled_egs_check())
    loop.run_forever()
except KeyboardInterrupt:
    print('[ERROR] exited manually')