from utils import DeckDownloader, DeckSender
import json
import os
import argparse

FILE_NAME = 'nextcloud-decks.json'

parser = argparse.ArgumentParser()

parser.add_argument('--mode')
parser.add_argument('--host', default="http://localhost:8080")
parser.add_argument('--username', default="test")
parser.add_argument('--passwd', default="test")
parser.add_argument('--directory', default=".")

args = parser.parse_args()
mode = args.mode
url = args.host
auth = (args.username, args.passwd)

if(mode == 'backup' or mode == None):
    dd = DeckDownloader(url, auth)

    data = dd.fetchBoards()

    with open(os.path.join(args.directory, FILE_NAME), 'w') as outfile:
        json.dump(data, outfile, indent=4)

    for warn in dd.getAllWarnings():
        print(warn)

elif(mode == 'send'):
    ds = DeckSender(url, auth)

    with open(os.path.join(args.directory, FILE_NAME)) as json_file:
        data = json.load(json_file)
        ds.sendBoard(data)

    for warn in ds.getAllWarnings():
        print(warn)

else:
    raise ValueError('Unknown mode or missing properites.')
