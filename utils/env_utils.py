import os
import requests

def refresh_access_token_twitch_generator(refresh_token):
    url = f"https://twitchtokengenerator.com/api/refresh/{refresh_token}"
    try:
        response = requests.get(url)
        response.raise_for_status()
        data = response.json()
        new_access_token = data.get("token")
        if new_access_token:
            update_env_file("BOT_TOKEN", new_access_token)
            return new_access_token
        return None
    except requests.RequestException as e:
        print("Error al renovar el access token:", e)
        return None

def update_env_file(key, value):
    with open('.env', 'r') as file:
        lines = file.readlines()
    with open('.env', 'w') as file:
        for line in lines:
            if line.startswith(f"{key}="):
                file.write(f"{key}={value}\n")
            else:
                file.write(line)
