import asyncio
import egs_module, tg_module

async def scheduled_egs_check():
    while True:
        if await asyncio.to_thread(egs_module.check_games_data):
            print('[INFO] data is being updated')
            await asyncio.to_thread(egs_module.game_data_update)
            print('[INFO] data was updated')
            await tg_module.notify_subscribers()
            print('[INFO] subscribers were notified')
        await asyncio.sleep(86400)

def main():
    loop = asyncio.get_event_loop()
    loop.create_task(scheduled_egs_check())
    tg_module.tg_handler()
    try:
        loop.run_forever()
    except KeyboardInterrupt:
        print('[ERROR] exited manually')

if __name__ == "__main__":
    main()