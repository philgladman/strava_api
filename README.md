# Step 1 - Create App
- Go to https://www.strava.com/settings/api
- Can use fake website domain
- Set `Authorization Callback Domain` to localhost

# Step 2 - Note down client details and secrets
- client id: 
- client secret: 
- access token: 
- refresh token: 

# Step 3 - Authorize app to read all 
- In a browser, go to the link below, replacing `REPLACE_WITH_YOUR_CLIENT_ID` with your client_id
- http://www.strava.com/oauth/authorize?client_id=REPLACE_WITH_YOUR_CLIENT_ID&response_type=code&redirect_uri=http://localhost/exchange_token&approval_prompt=force&scope=profile:read_all,activity:read_all
- Clink yes to authorize read all permissions
- This will return a page that does not exists. In the returned url, example below, copy the `TOKEN_FROM_URL`
- http://localhost/exchange_token?state=&code=TOKEN_FROM_URL&scope=read,activity:read_all,profile:read_all
