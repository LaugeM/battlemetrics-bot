import requests
import re

def get_player_info(player_id, bm_api_key, type):
    if type == "names":
        resp = requests.get(f"https://api.battlemetrics.com/players/{player_id}?include=identifier&access_token={bm_api_key}")
        name_list = []
        player_info = resp.json()
        for n in player_info["included"]:
            name_list.append(n["attributes"]["identifier"]+" last seen at: "+str(n["attributes"]["lastSeen"])+"\n")
    
        return name_list
    elif type == "hours":
        resp = requests.get(f"https://api.battlemetrics.com/players/{player_id}?include=server&fields[server]=name&access_token={bm_api_key}")
        hour_list = []
        player_servers = resp.json()
        all_servers = len(player_servers["included"])
        for n in player_servers["included"]:
            if n["relationships"]["game"]["data"]["id"] == "rust":
                hour_list.append(int(n["meta"]["timePlayed"]))
        return round(sum(hour_list)/3600), all_servers
    
    elif type == "server_count":
        resp = requests.get(f"https://api.battlemetrics.com/players/{player_id}?include=server&fields[server]=name&access_token={bm_api_key}")
        player_servers = resp.json()
        count = 0
        for n in player_servers["included"]:
            if n["relationships"]["game"]["data"]["id"] == "rust":
                count += 1
        return count
        
    elif type == "aim_hours":
        resp = requests.get(f"https://api.battlemetrics.com/players/{player_id}?include=server&fields[server]=name&access_token={bm_api_key}")
        hour_list = []
        player_servers = resp.json()
        for n in player_servers["included"]:
            if re.findall(r"ukn|aim", n["attributes"]["name"].lower()):
                if n["relationships"]["game"]["data"]["id"] == "rust":
                    hour_list.append(int(n["meta"]["timePlayed"]))
        return round(sum(hour_list)/3600)
    
    elif type == "info":
        resp = requests.get(f"https://api.battlemetrics.com/players/{player_id}?include=identifier&access_token={bm_api_key}")
        player_info = resp.json()
        info_list = []
        info_list.append(player_info["data"]["attributes"]["name"])
        info_list.append(player_info["data"]["attributes"]["createdAt"])
        return info_list
    elif type == "online":
        resp = requests.get(f"https://api.battlemetrics.com/players/{player_id}?include=server&fields[server]=name&access_token={bm_api_key}")
        player_servers = resp.json()
        for n in player_servers["included"]:
            if n["meta"]["online"] == True:
                return n["attributes"]["name"]
        return False
                
        

def convert_input(input):
    if input.isnumeric():
        return f'https://www.battlemetrics.com/players/{input}'
    elif "battlemetrics" in input:
        return input