from __future__ import print_function
import requests
import ujson

apiurl = 'https://www.peeringdb.com/api/'

# --------------- Helpers that build all of the responses ----------------------

def build_speechlet_response(title, output, reprompt_text, should_end_session):
    return {
        'outputSpeech': {
            #'type': 'PlainText',
            'type': 'SSML',
            #'text': output
            'ssml': '<speak>' + output + '</speak>'
        },
        'card': {
            'type': 'Simple',
            'title': "SessionSpeechlet - " + title,
            'content': "SessionSpeechlet - " + output
        },
        'reprompt': {
            'outputSpeech': {
                'type': 'PlainText',
                'text': reprompt_text
            }
        },
        'shouldEndSession': should_end_session
    }


def build_response(session_attributes, speechlet_response):
    return {
        'version': '1.0',
        'sessionAttributes': session_attributes,
        'response': speechlet_response
    }


# --------------- Functions that control the skill's behavior ------------------

# Basic function to fetch and parse
def fetchResults(url):
    try:
        response = requests.get(url)
        response = ujson.loads(response.text)
    except:
        response = None

    return response

def whoPeers(search):
    url = "%six?name=%s" % (apiurl, search)  # Try an exact match first

    results = requests.get(url)
    results = ujson.loads(results.text)

    # try an exact match on the long name
    if not results['data']:
        url = "https://www.peeringdb.com/api/ix?name_long=%s" % search
        results = requests.get(url)
        results = ujson.loads(results.text)

    # try a loose match
    if not results['data']:
        url = "https://www.peeringdb.com/api/ix?name__contains=%s" % search
        results = requests.get(url)
        results = ujson.loads(results.text)

    # try a loose match on the long name
    if not results['data']:
        url = "https://www.peeringdb.com/api/ix?name_long__contains=%s" % search
        results = requests.get(url)
        results = ujson.loads(results.text)

    if not results['data']:
        response = "Could not find %s" % search
    else:
        if len(results['data']) > 1:
            response = "Found multiple matches for %s" % search
        else:
            try:
                response = "Peering at %s is " % results['data'][0]['name_long']
            except:
                response = "Peering at %s is " % results['data'][0]['name']
            url = "https://www.peeringdb.com/api/ixlan?id=%s&depth=2" % (results['data'][0]['id'])
            results2 = requests.get(url)
            results2 = ujson.loads(results2.text)
            networks = []
            for x in results2['data'][0]['net_set']:
                networks.append(x['name'])

            # Sort and de-duplicate
            networks = sorted(set(networks))

            for net in networks:
                response = response + "<p>" + net + "</p>"

    speech_output = response
    reprompt_text = "Please try again"
    card_title = "Who Peers"
    session_attributes = {}
    should_end_session = True

    return build_response(session_attributes, build_speechlet_response(
        card_title, speech_output, reprompt_text, should_end_session))


def wherePeer(search):
    url = "%snet?name=%s&depth=2" % (apiurl, search)
    results = fetchResults(url)
    # Try explicit match first
    if not results['data']:
        url = "%snet?name__contains=%s&depth=2" % (apiurl, search)  # Then do loose match
        results = fetchResults(url)
    if not results['data']:
        response = "%s not found in PeeringDB" % (search)
    elif len(results['data']) > 1:
        response = "Found multiple entries for %s " % (search)
        for entry in results['data']:
            response = response + "<p>" + entry['name'] + "</p>"
    else:
        if len(results['data'][0]['netixlan_set']) < 1:
            response = results['data'][0]['name'] + " peers at"
            response = response + "<p>nowhere</p><p>because screw you, we're %s</p>" % results['data'][0]['name']
        else:
            if len(results['data'][0]['netixlan_set']) > 20:
                response = "Wow, %s peers a lot. They peer at " % results['data'][0]['name']
            else:
                response = results['data'][0]['name'] + " peers at"
            for ix in results['data'][0]['netixlan_set']:
                response = response + "<p>" + ix['name'] + "</p>"

    speech_output = response
    reprompt_text = "Please try again"
    card_title = "Where Peer"
    session_attributes = {}
    should_end_session = True

    return build_response(session_attributes, build_speechlet_response(
        card_title, speech_output, reprompt_text, should_end_session))

def whosAt(search):
    speech_output = "I'm sorry, this is not yet implemented"
    reprompt_text = "Please try again"
    card_title = "Who's At"
    session_attributes = {}
    should_end_session = True

    return build_response(session_attributes, build_speechlet_response(
        card_title, speech_output, reprompt_text, should_end_session))
def routeServers():

    speech_output = "<p>No one.</p><p>At least no one sensible</p>"
    reprompt_text = "Please try again"
    card_title = "Route Servers"
    session_attributes = {}
    should_end_session = True

    return build_response(session_attributes, build_speechlet_response(
        card_title, speech_output, reprompt_text, should_end_session))

# Matches an ASN and provides info
def whois(search):
    url = "%snet?asn=%s&depth=2" % (apiurl, search)
    results = fetchResults(url)
    if not results['data']:
        response = "A S %s not found in PeeringDB" % (asDigits(search))
    else:
        response = "A S %s is %s" % (asDigits(search), results['data'][0].pop('name'))
        if results['data'][0]['aka'] is not "":
            response = response + ", Also known as %s" % results['data'][0].pop('aka')

    speech_output = response
    reprompt_text = "Please try again"
    card_title = "Who Is"
    session_attributes = {}
    should_end_session = True

    return build_response(session_attributes, build_speechlet_response(
        card_title, speech_output, reprompt_text, should_end_session))

def asDigits(number):
    # silly function to wrap a number in "say-as" SSML tags
    return '<say-as interpret-as="digits">' + number + '</say-as>'

# --------------- Events ------------------


def on_intent(intent_request, session):
    """ Called when the user specifies an intent for this skill """

    intent = intent_request['intent']
    intent_name = intent_request['intent']['name']
    print(intent)

    # Dispatch to your skill's intent handlers
    if intent_name == "WhoIs":
        intent_search = intent['slots']['ASN']['value']
        return whois(intent_search)
    elif intent_name == "WherePeer":
        intent_search = intent['slots']['company']['value']
        return wherePeer(intent_search)
    elif intent_name == "WhoPeers":
        intent_search = intent['slots']['IX']['value']
        return whoPeers(intent_search)
    elif intent_name == "WhosAt":
        intent_search = intent['slots']['facility']['value']
        return whosAt(intent_search)
    elif intent_name == "RouteServers":
        return routeServers()
    else:
        raise ValueError("Invalid intent")


# --------------- Main handler ------------------

def lambda_handler(event, context):
    """ Route the incoming request based on type (LaunchRequest, IntentRequest,
    etc.) The JSON body of the request is provided in the event parameter.
    """
    print("event.session.application.applicationId=" +
          event['session']['application']['applicationId'])

    """
    Uncomment this if statement and populate with your skill's application ID to
    prevent someone else from configuring a skill that sends requests to this
    function.
    """
    #if (event['session']['application']['applicationId'] != "<APPLICATION_ID>"):
    #     raise ValueError("Invalid Application ID")


    if event['request']['type'] == "IntentRequest":
        return on_intent(event['request'], event['session'])