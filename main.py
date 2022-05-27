from utils import DeckDownloader
from dateparser import parse as parsedate
import argparse
import textwrap

parser = argparse.ArgumentParser()

parser.add_argument('--host', default="http://localhost:8080")
parser.add_argument('--username')
parser.add_argument('--passwd')
parser.add_argument('--deck')
parser.add_argument('--stack')
parser.add_argument('--textwidth', default=69)
parser.add_argument('--duration', help='time per agenda item, in minutes',
                    default=5)
parser.add_argument('--meetingtime', help='iso-formatted time and date')
parser.add_argument('--worldclockurl',
                    default=('https://www.timeanddate.com/worldclock/'
                             'converted.html?p1=37&p2=49&p3=107'))

args = parser.parse_args()
wrapper = textwrap.TextWrapper(width=args.textwidth,
                               drop_whitespace=False,
                               replace_whitespace=False,
                               tabsize=4,
                               break_long_words=False)
meeting_time = parsedate(args.meetingtime)

header = """
Dear Community,

find below the agenda for our

TDF board meeting with a public part, and followed by a private part on {0} at https://jitsi.documentfoundation.org/TDFBoard
For time zone conversion, see e.g. {1}

## AGENDA:

### Public Part

"""
header = header.format(
    meeting_time.strftime('%A, %B %d at %H%M Berlin time'),
    args.worldclockurl+"&iso="+meeting_time.strftime('%Y%m%dT%H'))
header = wrapper.fill(text=header)

item = 1
content = ""

# grab raw deck data
dd = DeckDownloader(args.host, (args.username, args.passwd))
data = dd.fetchBoards()

output = header

# dump public cards from proper list
for deck in data:
    if deck["title"] == args.deck:
        for stack in deck["stacks"]:
            if stack["title"] == args.stack and "cards" in stack:
                for card in stack["cards"]:
                    # cards with label 'private' - skip here
                    if not [x for x in card["labels"]
                            if x["title"] == 'private']:
                        labels = ", ".join(
                            [label['title']
                             for label in card["labels"]
                             if label["title"] != 'private'])
                        owners = ", ".join(
                            [user['participant']['displayname']
                             for user in card["assignedUsers"]])
                        if labels:
                            entry = f"{item}. {labels}: {card['title']} ({owners}, {args.duration} mins)"
                        else:
                            entry = f"{item}. {card['title']} ({owners}, {args.duration} mins)"
                        entry += "\n"
                        wrapper.initial_indent = '   '
                        wrapper.subsequent_indent = '   '
                        entry += wrapper.fill(f"{card['description']}")
                        entry += "\n"
                        item += 1
                        output += entry

output += """
### Private Part

"""

# dump private cards from proper list
for deck in data:
    if deck["title"] == args.deck:
        for stack in deck["stacks"]:
            if stack["title"] == args.stack and "cards" in stack:
                for card in stack["cards"]:
                    # cards with label 'private' - only pick those here
                    if [x for x in card["labels"] if x["title"] == 'private']:
                        labels = ", ".join(
                            [label['title'] for label in card["labels"]
                             if label["title"] != 'private'])
                        owners = ", ".join(
                            [user['participant']['displayname']
                             for user in card["assignedUsers"]])
                        if labels:
                            entry = f"{item}. {labels}: {card['title']} ({owners}, {args.duration} mins)"
                        else:
                            entry = f"{item}. {card['title']} ({owners}, {args.duration} mins)"
                        entry += "\n"
                        wrapper.initial_indent = '   '
                        wrapper.subsequent_indent = '   '
                        entry += wrapper.fill(f"{card['description']}")
                        entry += "\n"
                        item += 1
                        output += entry

footer = """
Total scheduled meeting time: {0} mins
"""
footer = footer.format((item-1)*args.duration)
output += footer

for warn in dd.getAllWarnings():
    print(warn)

print(output)
