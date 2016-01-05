from django.shortcuts import render
from django.http import HttpResponse, HttpResponseBadRequest
import requests
from main.models import Teams
from django.core.exceptions import ObjectDoesNotExist
from django.utils import timezone
import string
import random
from django.views.decorators.csrf import csrf_exempt
import os

# Create your views here.


def index(request):
    state = ''.join(random.choice(string.ascii_uppercase + string.digits) for _ in range(36))
    context = {"state": state}
    # TODO: track and verify state in cookie
    return render(request, "main/index.html", context)


client_id = "16839103392.17540259856"
client_secret = os.environ.get("SLACK_CLIENT_SECRET", "")


def oauthcallback(request):
    if "error" in request.GET:
        status = "Oauth authentication failed. You aborted the Authentication process. Redirecting back to the homepage..."
        context = {"status": status}
        return render(request, "main/oauthcallback.html", context)

    code = request.GET["code"]

    url = "https://slack.com/api/oauth.access"
    data = {
        "client_id": client_id,
        "client_secret": client_secret,
        "code": code,
    }

    r = requests.get(url, params=data)
    query_result = r.json()
    print query_result
    if query_result["ok"]:
        access_token = query_result["access_token"]
        team_name = query_result["team_name"]
        team_id = query_result["team_id"]

        try:
            team = Teams.objects.get(team_id=team_id)
        except ObjectDoesNotExist:
            # new Team (yay!)
            new_team = Teams(access_token=access_token, team_name=team_name, team_id=team_id, last_changed=timezone.now())
            new_team.save()
        else:
            team.access_token = access_token
            team.team_name = team_name
            team.save()

    else:
        status = "Oauth authentication failed. Redirecting back to the homepage..."
        context = {"status": status}
        return render(request, "main/oauthcallback.html", context)

    status = "Oauth authentication successful! You can now start using /poll. Redirecting back to the homepage..."
    context = {"status": status}
    return render(request, "main/oauthcallback.html", context)


@csrf_exempt
def poll(request):
    verifier = os.environ.get("SLACK_POLL_VERIFIER", "")
    if request.method != "POST":
        return HttpResponseBadRequest("400 Request should be of type POST.")
    try:
        sent_token = request.POST["token"]
    except KeyError:
        return HttpResponseBadRequest("400 Request is not signed!")
    else:
        if verifier != sent_token:
            return HttpResponseBadRequest("400 Request is not signed correctly!")
    data = request.POST["text"]

    items = data.split('"')

    print "items:", items
    question = items[1]
    options = []
    for i in range(1, len(items)+1):
        if i % 2 == 0 and i > 2:
            options.append(items[i-1])
    print "Options", options
    # all data ready for initial message at this point

    numbers = ["one", "two", "three", "four", "five", "six", "seven", "eight", "nine", "keycap_ten"]

    def sendPollMessage():

        text = ""
        text = "*" + question + "*\n\n"
        for option in range(0, len(options)):
            toAdd = ":" + numbers[option] + ":" + options[option] + "\n"
            text += str(toAdd)

        postMessage_url = "https://slack.com/api/chat.postMessage"
        postMessage_params = {
            "token": Teams.objects.get(team_id=request.POST["team_id"]).access_token,
            "text": text,
            "channel": request.POST["channel_id"],
            "username": "Simple Poll",
            "icon_url": "https://simplepoll.rocks/static/main/simplepolllogo-colors.png",
        }
        text_response = requests.post(postMessage_url, params=postMessage_params)

        print "Post message response:", text_response.text
        return text_response.json()["ts"]  # return message timestamp

    class ChannelDoesNotExist(Exception):
        def __init__(self, *args, **kwargs):
            Exception.__init__(self, *args, **kwargs)

    try:
        timestamp = sendPollMessage()
    except ChannelDoesNotExist:
        return HttpResponse("We cannot add reactions to the channel you posted to. You will have to add your own. Sorry!. :(")

    def addNumberReaction(number):

        reactions_url = "https://slack.com/api/reactions.add"

        reactions_params = {
            "token": Teams.objects.get(team_id=request.POST["team_id"]).access_token,
            "name": number,
            "channel": request.POST["channel_id"],
            "timestamp": timestamp
        }

        add_reaction = requests.get(reactions_url, params=reactions_params)

        print "Reaction add response", add_reaction.text

    for option in range(0, len(options)):
        addNumberReaction(numbers[option])

    return HttpResponse()  # Empty 200 HTTP response, to not display any additional content in Slack
