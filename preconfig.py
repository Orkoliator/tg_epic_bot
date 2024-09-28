import os
import yaml
import egs_module, sql_module

if os.name != 'nt':
    print("[INFO] non-Windows paths detected")
    app_path_divider = '/'
else:
    print("[INFO] Windows paths detected")
    app_path_divider = '\\'

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
        print (f"[INFO] found {env} in file")
        app_var_files = read_env_from_file()
        return app_var_files[env]

def preconfigure():
    api_id = set_env('TG_API_ID')
    api_hash = set_env('TG_API_HASH')
    bot_token = set_env('TG_BOT_TOKEN')

    for directory in ['pic_current', 'pic_upcoming']:
        if not os.path.exists(os.path.dirname(__file__) + app_path_divider + directory):
            os.makedirs(os.path.dirname(__file__) + app_path_divider + directory)

    sql_module.set_db()

    return api_id, api_hash, bot_token