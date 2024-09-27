import os
from flask import Flask, redirect, request, session, url_for, render_template
import requests
from datetime import datetime

app = Flask(__name__)
app.secret_key = os.urandom(24)

DISCORD_CLIENT_ID = '1287063898721222738'
DISCORD_CLIENT_SECRET = 'r-Abuwn8pzMM_hqu6-qJYqVfbBc65B-L'
DISCORD_REDIRECT_URI = 'http://localhost:5000/callback'
DISCORD_BOT_TOKEN = 'MTI4NzA2Mzg5ODcyMTIyMjczOA.GiYwn6.xau4kOD3Ra2g2f4gl9jcUmpd8TdeB6GCaoNUaA'  # Replace with your actual bot token
GUILD_ID = '1253093677606244472'  # The ID of your Discord server
ROLE_ID = '1262504011094032485'  # The ID of the role to assign

LOG_FILE_PATH = 'user_log.txt'

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/login')
def login():
    return redirect(
        f'https://discord.com/api/oauth2/authorize?client_id={DISCORD_CLIENT_ID}&redirect_uri={DISCORD_REDIRECT_URI}&response_type=code&scope=identify'
    )

@app.route('/callback')
def callback():
    code = request.args.get('code')

    data = {
        'client_id': DISCORD_CLIENT_ID,
        'client_secret': DISCORD_CLIENT_SECRET,
        'grant_type': 'authorization_code',
        'code': code,
        'redirect_uri': DISCORD_REDIRECT_URI,
        'scope': 'identify'
    }

    headers = {
        'Content-Type': 'application/x-www-form-urlencoded',
    }

    response = requests.post('https://discord.com/api/oauth2/token', data=data, headers=headers)
    token_data = response.json()

    if response.status_code != 200:
        return f'Error obtaining access token: {token_data.get("error_description", "Unknown error")}'
    
    access_token = token_data.get('access_token')
    if access_token:
        user_response = requests.get(
            'https://discord.com/api/v10/users/@me',
            headers={'Authorization': f'Bearer {access_token}'}
        )
        
        user_data = user_response.json()

        if user_response.status_code != 200:
            return f'Error obtaining user information: {user_data.get("error_description", "Unknown error")}'
        
        user_id = user_data['id']
        assign_role(user_id)

        log_to_file(user_data)

        return render_template('index.html', username=user_data["username"], discriminator=user_data["discriminator"])

    return 'Error: No access token in response'

def assign_role(user_id):
    url = f"https://discord.com/api/v10/guilds/{GUILD_ID}/members/{user_id}/roles/{ROLE_ID}"
    headers = {
        'Authorization': f'Bot {DISCORD_BOT_TOKEN}'
    }
    response = requests.put(url, headers=headers)

    if response.status_code != 204:
        print(f"Failed to assign role: {response.text}")
    else:
        print("Role assigned successfully.")

def log_to_file(user_data):
    date_str = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    logged_users_count = 0

    if os.path.exists(LOG_FILE_PATH):
        with open(LOG_FILE_PATH, 'r') as log_file:
            logged_users_count = sum(1 for _ in log_file)

    log_entry = f"|   {logged_users_count + 1} | {date_str} | {user_data['username']} | {user_data['id']} | '.gg/wyciek'|\n"

    with open(LOG_FILE_PATH, 'a') as log_file:
        log_file.write(log_entry)

    print(f"Successfully logged user data to file. Total verified users: {logged_users_count + 1}.")

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)