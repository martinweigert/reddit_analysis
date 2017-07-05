import json
import requests
import requests.auth
import pprint
import time
import matplotlib.pyplot as plt
from matplotlib import style

# This script accesses a specified subreddit on Reddit and tracks the number of upvotes
# for a specified number of the top posts at that time. The upvotes will be saved in txt files.
# The script also offers the option to plot the graphs righ taway, frequently updated.
# I had problems with using Matplot's interactive mode (ION()) and the .draw() command.
# Therefore I rely on the .show() command every 3 minutes and force it to close after 60 seconds. It's not
# ideal because it keeps popping up into the foreground every time it loads.
# I might find a solution for it later.

# reddit requesting authentification with username, password, client id and reddit secret tutorial:
# https://github.com/reddit/reddit/wiki/OAuth2
# https://github.com/reddit/reddit/wiki/OAuth2-Quick-Start-Example
# https://www.reddit.com/r/redditdev/ ask there for help if you have problems.


items_tracked = 10 # adjust here how many items from the 'new' section should be tracked (descending).
subreddit = "The_Donald" # enter any name for the subreddit. Must be exactly how it is written on reddit.com.

# reddit oauth authentification procedure
# see tutorial to learn how to obtain the following data:
# https://github.com/reddit/reddit/wiki/OAuth2-Quick-Start-Example

app_client_id = "XXX"
app_secret = "XXX"
reddit_username = "XXX"
reddit_password = "XXX"

client_auth = requests.auth.HTTPBasicAuth(app_client_id, app_secret)
post_data = {"grant_type": "password", "username": reddit_username, "password": reddit_password}
headers = {"User-Agent": "graph plotting v0.1 (by /u/YourUsername)"}
response = requests.post("https://www.reddit.com/api/v1/access_token", auth=client_auth, data=post_data, headers=headers)
response.raise_for_status()
token = response.json()['access_token']
headers = {'Authorization': 'Bearer ' + token, "User-Agent": "graph plotting v0.1 (by /u/YourUsername)"}
response = requests.get("https://oauth.reddit.com/api/v1/me", headers=headers)
response.raise_for_status()

# file-to_list function prepares the tracked upvotes for the lists used for plotting

def file_to_list(file,number,title,score):
    list = []
    with open(file, "a") as file_scores:
        if counter_dict[number] == 0:
            first_line = ("%s" % title)
            pprint.pprint(first_line, file_scores)
            major_list.append([])
            major_list[number-1].append(title)
            counter_dict[number] += 1
        pprint.pprint(score, file_scores)
        major_list[number-1].append(score)

# plot function handles the plotting

def plot():
    timestamp = []
    for item in range(len(major_list[0])):
        timestamp.append(item)

    style.use('fivethirtyeight')

    font = {'family' : 'arial',
            'weight' : 'light',
            'size'   : 8}

    plt.rc('font', **font)

    for index in range(items_tracked):
        plt.plot(timestamp[0:-1],major_list[index][1:], label=major_list[index][0])

    plt.xlabel('time (in minutes)')
    plt.ylabel('Upvotes')
    plt.title('Upvotes over time for top posts at reddit.com/r/%s' % subreddit)
    plt.legend(loc=2,prop={'size':7})
    plt.ylim(ymin=0) # remove if y-axis should not be forced to start at 0.
    plt.show(block = False)


user_input_plot = input("Do you want to plot 'live'? Type 'y'. Any other key will only save upvotes to txt files: ")
print("Thank you. Accessing the data...")


# will be needed in order to regularly "live" plot.

starttime=time.time()
count_for_plotting = 0

major_list = [] # will store lists with the scores for each item.


# accessing the necessary data from these stories.

headers = {'Authorization': 'Bearer ' + token,
        "User-Agent": "reddit graph plotting v0.1 (by /u/YourUsername)"}
url = ('https://oauth.reddit.com/r/%s/.json' % subreddit)
posts_all = requests.get(url, headers=headers)
posts_all.raise_for_status()
reddit = json.loads(posts_all.text)


# creating the list to store the permalinks to the top articles

list_w_permalinks = []

for i in range(10):
    permalink = reddit['data']['children'][i]['data']['permalink']
    list_w_permalinks.append(permalink)


# counter_dict is used later to ensure that the post's title is only printed to the txt file once

counter_dict = {}
for num in range(len(list_w_permalinks)):
    counter_dict[num+1] = 0


# accessing the title and upvotes from each file, handing it to the file_to_list function
# repeating this procedure every 60 seconds.

while True:
    for number, link in enumerate(list_w_permalinks):
        post_url = ("https://oauth.reddit.com/%s.json" % link)
        post = requests.get(post_url, headers=headers)
        post.raise_for_status()
        item = json.loads(post.text)
        ups = item[0]['data']['children'][0]['data']['ups']
        title = item[0]['data']['children'][0]['data']['title']
        file = "reddit_score_item%s.txt" % (number+1)
        file_to_list(file,number+1,title[0:50],ups)
    count_for_plotting += 1
    print("working #%s" % count_for_plotting)
    if user_input_plot.startswith("y"):
        if count_for_plotting % 3 == 0:
            plot()
    time.sleep(60.0 - ((time.time() - starttime) % 60.0))
    plt.close()
