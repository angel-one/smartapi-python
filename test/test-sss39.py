import pyotp
import pandas as pd
import numpy as np
from SmartApi import SmartConnect

# Hardcoded values
token = "XXXXXXXXXXXXXXXXXXXXXXXXXX"
apikey = "XXXXXX"
ClientID = "XXXXXXX"
totp = pyotp.TOTP(token).now()
paswrd = "XXXX"

# Print values and their types
print(ClientID, paswrd, totp, type(ClientID), type(paswrd), type(totp))
print(ClientID, paswrd, totp, len(str(ClientID)), len(str(paswrd)), len(str(totp)))

# Create an instance of SmartConnect
obj = SmartConnect(api_key=apikey)

# Login API call
data = obj.generateSession(ClientID, paswrd, totp)
refreshToken = data['data']['refreshToken']
feedToken = obj.getfeedToken()

# Fetch User Profile
userProfile = obj.getProfile(refreshToken)

# Reading data from CSV and manipulating values
Client_2_ftech = 'RKRPA1227'
user_df = pd.read_csv("ClientDetails.csv")

ClientID = user_df[user_df['ClientID'] == Client_2_ftech]['ClientID'].values
ClientID = np.array_str(ClientID)
ClientID = ClientID.replace(' ', '')
ClientID = ClientID.replace('[', '')
ClientID = ClientID.replace(']', '')
ClientID = ClientID.replace("'", '')

paswrd = user_df[user_df['ClientID'] == Client_2_ftech]['PassKey'].values
paswrd = np.array_str(paswrd)
paswrd = paswrd.replace('[', '')
paswrd = paswrd.replace(']', '')

APIkey = user_df[user_df['ClientID'] == Client_2_ftech]['APIkey'].values
APIkey = np.array_str(APIkey)
APIkey = APIkey.replace('[', '')
APIkey = APIkey.replace(']', '')
APIkey = APIkey.replace("'", '')

token = user_df[user_df['ClientID'] == Client_2_ftech]['token'].values
token = np.array_str(token)
token = token.replace(' ', '')
token = token.replace('[', '')
token = token.replace(']', '')
token = token.replace("'", '')

totp = pyotp.TOTP(token).now()

# Create a new instance of SmartConnect with updated values
obj = SmartConnect(api_key=APIkey)

# Print updated values and their types
print(ClientID, paswrd, totp, type(ClientID), type(paswrd), type(totp))
print(ClientID, paswrd, totp, len(str(ClientID)), len(str(paswrd)), len(str(totp)))

# Call the generateSession method
data = obj.generateSession(ClientID, paswrd, totp)
