"""
app.py
Description: This Flask application is designed to block spam phone calls by analyzing data provided by various third-party services (add-ons).

Contents:
1. Initialize the Flask application route
2. Incorporate add-ons from Twilio marketplace
3. Define the function logic
4. Helper functions

The Python app listens for POST requests from Twilio. It checks the call data against various third-party services to determine if the call is spam. If any service flags the call as spam, the app rejects the call.
If the call is not spam, it plays a message and hangs up. The helper functions determine whether a call should be blocked based on the results from Nomorobo, Ekata, and Marchex services.

"""

#!/usr/bin/env python3
from flask import Flask, request
from twilio.twiml.voice_response import VoiceResponse
import json

# 1. Initialize the Flask application route
# After initializing the Flask application, a route "/" is defined to handle incoming POST requests. 
# The "resp" variable initializes a Twilio VoiceResponse object, which will be used to generate the response that will be sent back to Twilio to control the call. 
# "block_call = False:" Initializes a flag to determine if the call should be blocked.

app = Flask(__name__)

@app.route("/", methods=['POST'])
def block_spam_calls():
    resp = VoiceResponse()
    block_call = False

# 2. Incorporate add-ons from Twilio marketplace
# This dictionary maps the names of the third-party services (Nomorobo, Ekata, Marchex) to their respective functions (should_be_blocked_by_nomorobo, should_be_blocked_by_ekata, and should_be_blocked_by_marchex). 
# Each of these functions will decide whether the call should be blocked based on the results from these services.

    blocker_addons = {
        "nomorobo_spamscore": should_be_blocked_by_nomorobo,
        "ekata_phone_valid": should_be_blocked_by_ekata,
        "marchex_cleancall": should_be_blocked_by_marchex
    }
    
# 3. Define the function logic
# This if statement checks if the incoming request contains data from Twilio add-ons (third-party services that analyze the call and provide spam scores or other reputation data).
# The data is parsed into a Python dictionary and loops through each add-on to determine if the parsing was successful. 
# If the add-ons have determined that the call should be blocked, then the "block_call" flag is set to True. The call will then be rejected using the built in "reject()" function from the Twilio VoiceResponse package. 
# Otherwise, the call is not flagged as spam and it plays a message saying "Welcome to the jungle" and hangs up after. The function returns a enerated TwiML response as a string.

    if 'AddOns' in request.form:
        add_ons = json.loads(request.form['AddOns'])
        if add_ons['status'] == 'successful':
            for blocker_name, blocker_func in blocker_addons.items():
                should_be_blocked = blocker_func(add_ons['results'].get(blocker_name, {}))
                # print(f'{blocker_name} should be blocked ? {should_be_blocked}')
                block_call = block_call or should_be_blocked

    if block_call:
        resp.reject()
    else:
        resp.say("Welcome to the jungle.")
        resp.hangup()
    return str(resp)

# 4. Helper functions
# # If any service flags the call as spam, the app rejects the call using the respective extension's built in conditions. 

def should_be_blocked_by_nomorobo(nomorobo_spamscore):
    if nomorobo_spamscore.get('status') != 'successful':
        return False
    else:
        score = nomorobo_spamscore['result'].get('score', 0)
        return score == 1


def should_be_blocked_by_ekata(ekata):
    if ekata.get('status') != 'successful':
        return False
    return ekata['result']['reputation_level'] >= 4


def should_be_blocked_by_marchex(marchex):
    if marchex.get('status') != 'successful':
        return False

    recommendation = marchex.get('result', {}).get('result', {}).get('recommendation')
    return recommendation == 'BLOCK'


if __name__ == "__main__":
    app.run(debug=True, host='0.0.0.0')
