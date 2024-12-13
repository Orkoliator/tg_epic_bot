from async_cron.job import CronJob
from async_cron.schedule import Scheduler
import asyncio
import egs_module, tg_module

async def egs_update():
    if egs_module.check_games_data():
        egs_module.game_data_update()
        await tg_module.notify_subscribers()

scheduler = Scheduler(locale="pl-PL")
egs_update_task = CronJob(name='egs_update').every().day.at("20:44").go(egs_update)

def main():
    loop = asyncio.get_event_loop()
    scheduler.add_job(egs_update_task)
    tg_module.tg_handler()
    try:
        loop.run_until_complete(scheduler.start())
    except KeyboardInterrupt:
        print('[ERROR] exited manually')

if __name__ == "__main__":
    main()