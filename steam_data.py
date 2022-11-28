from urllib import response
import requests


def convertID(input, type):
    resp = requests.get(f'https://converter.api.dedns.org/{input}')
    if resp.status_code == 200:
        data = resp.json()
        if type == "url":
            return data["data"]["steam_url"]
        elif type == "id":
            return data["data"]["steam_id64"]
    else:
        print("Got no response from converter.tools.dedns.org")


def grabProfileData(steamID, info, key):
    resp = requests.get(
        "https://api.steampowered.com/ISteamUser/GetPlayerSummaries/v0002/?key="
        + key + "&steamids=" + steamID)
    if resp.status_code == 200:
        data = resp.json()
        try:
            if info == "name":
                return data["response"]["players"][0]["personaname"]
            elif info == "avatar":
                return data["response"]["players"][0]["avatarfull"]
            elif info == "visiblity":
                return data["response"]["players"][0]["communityvisibilitystate"]
        except:
            print("Error: Probably not a valid steamID")
            return False
    else:
        print("Got no response from Steam")