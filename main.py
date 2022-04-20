from utils import DeckDownloader, DeckSender
import os
import argparse
import csv

FILE_NAME = 'nextcloud-decks.csv'

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
        fieldnames = ["#","Project","Tracker","Parent task","Parent task subject",
                      "Status","Priority","Subject","Description","Author","Assignee","Updated",
                      "Category","Sprint/Milestone","Start date","Due date",
                      "Estimated time","Total estimated time","Spent time","Total spent time",
                      "% Done","Created","Closed","Last updated by","Related issues","Files",
                      "Checklist","PSP-Element","Private","Story points","Taskboard position",
                      "Company","Contact person"]
        csv_out = csv.DictWriter(outfile, fieldnames=fieldnames)
        csv_out.writeheader()
        for deck in data:
            for stack in deck["stacks"]:
                if "cards" in stack:
                    for card in stack["cards"]:
                        csv_out.writerow({'#': card["id"],
                                          'Project': deck["title"],
                                          'Status': stack["title"],
                                          'Subject': card["title"],
                                          'Description': card["description"],
                                          'Updated': card["lastModified"],
                                          'Due date': card["duedate"]})

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
