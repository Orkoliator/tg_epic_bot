from telethon import TelegramClient, events
from telethon.tl.types import PeerUser, PeerChat, PeerChannel
import os
import yaml
import egs_module

if os.name != 'nt':
    app_path_divider = '/'
else:
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
        print(f'ERROR\ncannot find variables\nerror message: {exception}')
        return None

def set_env(env):
    if os.getenv(env):
        print (f'found {env} in system environment')
        return os.environ[env]
    else:
        return app_var_files[env]

app_var_files = read_env_from_file()
api_id = set_env('TG_API_ID')
api_hash = set_env('TG_API_HASH')
bot_token = set_env('TG_BOT_TOKEN')
client = TelegramClient('bot_session', api_id, api_hash).start(bot_token=bot_token)

@client.on(events.NewMessage(pattern='^/start$'))
async def handle_start_command(event):
    chat_id = event.message.peer_id
    if isinstance(chat_id, (PeerUser)):
        await client.send_message(chat_id, 'Hello friend, my name is Epic Bot. I monitor EGS free games info and share it. Please use /start_subscription@epic_announcement_bot command and I will start sharing this information in this chat, or add me to chat and start me with same command!')

@client.on(events.NewMessage(pattern='^/start_subscription@epic_announcement_bot$'))
async def handle_start_command(event):
    chat_id = event.message.peer_id
    if isinstance(chat_id, (PeerChat, PeerChannel)):
        await client.send_message(chat_id, 'Hello team, my name is Epic Bot and I\'m going to share an information about EGS free games with you here!')
        print(f' chat to be added: {chat_id}')
    elif isinstance(chat_id, (PeerUser)):
        await client.send_message(chat_id, 'Now I will start sharing EGS free games data with you!')

@client.on(events.NewMessage(pattern='^/stop_subscription@epic_announcement_bot$'))
async def handle_start_command(event):
    chat_id = event.message.peer_id
    if isinstance(chat_id, (PeerChat, PeerChannel)):
        await client.send_message(chat_id, 'Got it, no more information about free games needed. See ya, team!')
        print(f' chat to be removed: {chat_id}')
    elif isinstance(chat_id, (PeerUser)):
        await client.send_message(chat_id, 'Got it, no more information about free games needed. See ya, friend!')

@client.on(events.NewMessage(pattern='^/egs_status@epic_announcement_bot$'))
async def handle_start_command(event):
    chat_id = event.message.peer_id
    status = egs_module.check_egs()
    await client.send_message(chat_id, f'EGS status: {status}')

@client.on(events.NewMessage(pattern='^/current_games@epic_announcement_bot$'))
async def handle_start_command(event):
    chat_id = event.message.peer_id
    if isinstance(chat_id, (PeerUser, PeerChat, PeerChannel)):
        try:
            message_text, urls = egs_module.get_current_games_data()
            await client.send_file(chat_id, urls, caption=message_text)
        except Exception as exception:
            print(exception)
            await client.send_message(chat_id, 'Something went wrong, please check store status with /egs_status@epic_announcement_bot command')

@client.on(events.NewMessage(pattern='^/upcoming_games@epic_announcement_bot$'))
async def handle_start_command(event):
    chat_id = event.message.peer_id
    if isinstance(chat_id, (PeerUser, PeerChat, PeerChannel)):
        try:
            message_text, urls = egs_module.get_upcoming_games_data()
            await client.send_file(chat_id, urls, caption=message_text)
        except Exception as exception:
            print(exception)
            await client.send_message(chat_id, 'Something went wrong, please check store status with /egs_status@epic_announcement_bot command')

with client:
    client.run_until_disconnected()