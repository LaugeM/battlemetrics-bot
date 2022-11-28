import inspect
import os.path


def read_config():

    myDic = {}

    try:
        from configparser import ConfigParser
    except ImportError:
        from configparser import ConfigParser  # ver. < 3.0

    # instantiate
    config = ConfigParser()

    filename = inspect.getframeinfo(inspect.currentframe()).filename
    path = os.path.dirname(os.path.abspath(
        filename)) + "/Setup/config.ini"
    print("Config Path :" + path)

    # parse existing file
    config.read(path)

    bot_id = config.get('section_a', 'bot_id')
    myDic['bot_id'] = bot_id

    bm_api_key = config.get(
        'section_a', 'bm_api_key')
    myDic['bm_api_key'] = bm_api_key
    
    steam_api_key = config.get('section_a', 'steam_api_key')
    myDic['steam_api_key'] = steam_api_key
        

    return myDic