# The MIT License (MIT)
#
# Copyright (c) 2016 James Slagle <james.slagle@gmail.com>
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in all
# copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.

import argparse
from datetime import datetime
from pprint import pprint
import requests

class Trello(object):

    def __init__(self, api_key, api_token):
        self.url = "https://api.trello.com/1/%s"
        self.api_key = api_key
        self.api_token = api_token
        self.payload = dict(key=self.api_key, token=self.api_token)

    def get(self, path):
        r = requests.get(self.url % path, params=self.payload)
        return r.json()

parser = argparse.ArgumentParser()
parser.add_argument("--api-key",
                    required=True,
                    help="Trello API key")
parser.add_argument("--api-token",
                    required=True,
                    help="Trello API token")
parser.add_argument("--board-name",
                    required=True,
                    help="Board name on which to report")
args = parser.parse_args()

trello = Trello(args.api_key, args.api_token)
board = [b for b in trello.get("/member/me/boards") \
            if b["name"] == args.board_name][0]
board_id = board["id"]
lists = trello.get("/boards/%s/lists" % board_id)

next_list = [l for l in lists if l["name"] == "Next"][0]
next_list_id = next_list["id"]
next_cards = trello.get("/lists/%s/cards" % next_list_id)

in_progress_list = [l for l in lists if l["name"] == "In Progress"][0]
in_progress_list_id = in_progress_list["id"]
in_progress_list_cards = trello.get("/lists/%s/cards" % in_progress_list_id)

dev_complete_list = [l for l in lists if l["name"] == "Dev Complete"][0]
dev_complete_list_id = dev_complete_list["id"]
dev_complete_list_cards = trello.get("/lists/%s/cards" % dev_complete_list_id)

qe_accepted_list = [l for l in lists if l["name"] == "QE Accepted (Done)"][0]
qe_accepted_list_id = qe_accepted_list["id"]
qe_accepted_list_cards = trello.get("/lists/%s/cards" % qe_accepted_list_id)

all_cards = trello.get("/boards/%s/cards" % board_id)

def print_card(card):
    due = card["due"]
    if due is not None:
        due = datetime.strptime(card["due"],
                "%Y-%m-%dT%H:%M:%S.%fZ")
        due = due.strftime("%B %d, %Y")
    print("# - %s" % card["name"])
    print("#   Due: %s" % due)
    print("#   Link: %s" % card["shortUrl"])
    members = [str(trello.get("/members/%s/fullName" % id)["_value"]) for
               id in card["idMembers"]]
    members = ', '.join(members)
    if not members:
        members = "None"
    print ("#   Members: %s" % members)

print("This report provides a daily summary of Trello status.")
print

print("####################################################################")
print("# Blocked Epics:")
print("#")
blocked = 0
for card in next_cards:
    label_names = [n["name"] for n in card["labels"]]
    if "Blocked" in label_names and "EPIC" in label_names:
        print_card(card)
        blocked += 1
print("#")
print("# Summary: %d epics are blocked" % blocked)
print("####################################################################")
print
print


print("####################################################################")
print("# Epics requiring PM input:")
print("#")
pm_input = 0
for card in all_cards:
    label_names = [n["name"] for n in card["labels"]]
    if "PM Input needed" in label_names and "EPIC" in label_names:
        print_card(card)
        pm_input += 1
print("#")
print("# Summary: %d epics require PM input" % pm_input)
print("####################################################################")
print
print


print("####################################################################")
print("# Epics off track due to lack of owner:")
print("#")
no_owner = 0
for card in next_cards:
    label_names = [n["name"] for n in card["labels"]]
    if card["idMembers"] == [] and "EPIC" in label_names:
        print_card(card)
        no_owner += 1
print("#")
print("# Summary: %d epics are off track due to lack of owner" %
      no_owner)
print("####################################################################")
print
print

print("####################################################################")
print("# Epics off track with an owner but not in progress:")
print("#")
not_in_progress = 0
for card in next_cards:
    label_names = [n["name"] for n in card["labels"]]
    if card["idMembers"] and "EPIC" in label_names:
        print_card(card)
        not_in_progress += 1
print("#")
print("# Summary: %d epics are off track due to not in progress" %
      not_in_progress)
print("####################################################################")
print
print

print("####################################################################")
print("# Epics otherwise off track:")
print("#")
off_track = 0
for card in in_progress_list_cards:
    label_names = [n["name"] for n in card["labels"]]
    if "Off Track" in label_names and "EPIC" in label_names:
        print_card(card)
        off_track += 1
print("#")
print("# Summary: %d epics are otherwise off track" %
      off_track)
print("####################################################################")
print
print

print("####################################################################")
print("# Epics in progress: ")
print("#")
in_progress = 0
for card in in_progress_list_cards:
    label_names = [n["name"] for n in card["labels"]]
    if "Off Track" not in label_names and "EPIC" in label_names:
        print_card(card)
        in_progress += 1
print("#")
print("# Summary: %d epics are in progress" %
      in_progress)
print("####################################################################")
print
print

print("####################################################################")
print("# Epics dev complete:")
print("#")
dev_complete = 0
for card in dev_complete_list_cards:
    label_names = [n["name"] for n in card["labels"]]
    if "EPIC" in label_names:
        print_card(card)
        dev_complete += 1
print("#")
print("# Summary: %d epics are dev complete" % dev_complete)
print("####################################################################")
print
print

print("####################################################################")
print("# Epics qe accepted:")
print("#")
qe_accepted = 0
for card in qe_accepted_list_cards:
    label_names = [n["name"] for n in card["labels"]]
    if "EPIC" in label_names:
        print_card(card)
        qe_accepted += 1
print("#")
print("# Summary: %d epics are qe accepted" % qe_accepted)
print("####################################################################")
print
print

print("This report generated with trud: https://github.com/slagle/trud")
print
