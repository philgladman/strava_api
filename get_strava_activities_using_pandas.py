import requests
import json
import os
import time
from datetime import datetime
from pandas import json_normalize
import pandas as pd

from requests_oauthlib import OAuth2Session
from dotenv import load_dotenv
# import os

load_dotenv()
client_id = os.getenv('CLIENT_ID')
client_secret = os.environ.get('CLIENT_SECRET')
redirect_url = "https://localhost/exchange_token"
strava_tokens_outfile = ".strava_tokens.json"
strava_activities_outfile = "strava_activities.csv"

def save_token(session_token):
        # Save json response as a variable
    strava_tokens = session_token
    # Save tokens to file
    with open(strava_tokens_outfile, 'w') as outfile:
        json.dump(strava_tokens, outfile)
    # Print the tokens to screen to confirm authentication was successful
    print(strava_tokens)

def get_auth_toke():
    session = OAuth2Session(client_id=client_id, redirect_uri=redirect_url)

    auth_base_url = "https://www.strava.com/oauth/authorize"
    session.scope = ["profile:read_all,activity:read_all"]
    auth_link = session.authorization_url(auth_base_url)

    print(f"\nClick Here!!! {auth_link[0]}\n")

    redirect_response = input(f"Paste redirect url here: ")

    token_url = "https://www.strava.com/api/v3/oauth/token"
    session.fetch_token(
        token_url=token_url,
        client_id=client_id,
        client_secret=client_secret,
        authorization_response=redirect_response,
        include_client_id=True
    )
    save_token(session.token)

def get_access_token(file):
    """Get the access token from strava_tokens_outfile to connect to Strava"""
    with open(file) as json_file:
        strava_tokens = json.load(json_file)

    return strava_tokens

def update_expired_access_token():
    """Make Strava auth API call with current refresh token to update expired token"""
    session = OAuth2Session(client_id=client_id, redirect_uri=redirect_url)

    token_url = "https://www.strava.com/api/v3/oauth/token"
    session.refresh_token(
        token_url=token_url,
        client_id=client_id,
        client_secret=client_secret,
        refresh_token=get_access_token(strava_tokens_outfile)['refresh_token']
    )
    save_token(session.token)

def get_activities_and_create_csv():
    url = "https://www.strava.com/api/v3/activities"
    access_token = get_access_token(strava_tokens_outfile)['access_token']

    # Create the dataframe ready for the API call to store your activity data
    activities_df = pd.DataFrame(
        columns = [
                "Date",
                "Name",
                "Type",
                "Distance_in_Miles",
                "Time_in_Hours",
                "Time_in_Minutes",
                "Pace_in_mph",
                "Pace_in_Minutes_per_Mile"
        ]
    )

    # Loop through all activities
    page = 1

    while True:
        full_activities_data = requests.get(url + '?access_token=' + access_token + '&per_page=200' + '&page=' + str(page))
        full_activities_data_json = full_activities_data.json()
        full_activities_data_df = json_normalize(full_activities_data_json)
        if 'Rate Limit Exceeded' in full_activities_data_df:
            print("ERROR: RATE LIMIT REACHED")
            break

        # if no results then exit loop
        if (not full_activities_data_json):
            print("Complete: No more pages to iterate thru, exiting loop")
            break

        for i in range(len(full_activities_data_df)):
            # Set variables
            unformatted_start_date_local= datetime.strptime(full_activities_data_df['start_date_local'].iloc[i], '%Y-%m-%dT%H:%M:%S%z')
            formatted_start_date_local = datetime.strftime(unformatted_start_date_local, '%m-%d-%Y %H:%M:%S')
            name = full_activities_data_df['name'].iloc[i]
            type = full_activities_data_df['type'].iloc[i]
            elapsed_time = full_activities_data_df['elapsed_time'].iloc[i]
            distance_in_miles = round((full_activities_data_df['distance'].iloc[i] / 1609.344), 2)
            time_in_hr = round((elapsed_time / 60 / 60), 2)
            time_in_min = round((elapsed_time / 60), 2)
            if distance_in_miles != 0:
                pace_in_mph = round((distance_in_miles / time_in_hr), 2)
                pace_in_min_per_mile = round((time_in_min / distance_in_miles), 2)
            else:
                pace_in_mph = 0
                pace_in_min_per_mile = 0

            # Set new row with each variable
            new_row = pd.DataFrame({'Date': formatted_start_date_local, 
                                    'Name': name, 
                                    'Type': type, 
                                    'Distance_in_Miles': distance_in_miles, 
                                    'Time_in_Hours': time_in_hr, 
                                    'Time_in_Minutes': time_in_min, 
                                    'Pace_in_mph': pace_in_mph, 
                                    'Pace_in_Minutes_per_Mile': pace_in_min_per_mile}, 
                                    index=[i])
            
            # Add new row to dataframe
            activities_df = pd.concat([new_row,activities_df.loc[:]]).reset_index(drop=True)
        page += 1
        activities_df.to_csv(strava_activities_outfile)

if os.path.isfile(strava_tokens_outfile):
    expiration_date = get_access_token(strava_tokens_outfile)['expires_at']
    if expiration_date > time.time():
        print("Access token still valid, using existing access token from file")
    else:
        print("Access token has expired, generating new one form Strava")
        update_expired_access_token()
    get_activities_and_create_csv()
else:
    print("No auth file found! Authenticating to strava and creating auth file")
    get_auth_toke()
    get_activities_and_create_csv()
