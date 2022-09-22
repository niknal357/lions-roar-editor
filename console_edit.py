import sys
import subprocess
import json
import time
from datetime import date
import datetime
import math
from os import system, name
import os

tags_types = [
    "Upper School",
    "Middle School",
    "Lower School",
    "Sport",
    "Science",
    "Math",
    "English",
    "German",
    "French",
    "Spanish",
    "Physics"
]


art_types = ["video", "image", "audio", "text", "link"]


def next_weekday(d, weekday):
    days_ahead = weekday - d.weekday()
    if days_ahead <= 0:  # Target day already happened this week
        days_ahead += 7
    return d + datetime.timedelta(days_ahead)


def clear():
    # for windows
    if name == 'nt':
        _ = system('cls')

    # for mac and linux
    else:
        _ = system('clear')


def week_of_month(dt):
    """ Returns the week of the month for the specified date.
    """

    first_day = dt.replace(day=1)

    dom = dt.day
    adjusted_dom = dom + first_day.weekday()

    return int(math.ceil(adjusted_dom/7.0))


def install(package):
    subprocess.check_call([sys.executable, "-m", "pip", "install", "--trusted-host", "pypi.org",
                          "--trusted-host", "pypi.python.org", "--trusted-host", "files.pythonhosted.org", package])


try:
    from github import Github
except ImportError:
    install("PyGithub")
    exit(1)

try:
    import pick
except ImportError:
    install("pick")
    exit(1)

try:
    from tkinter import Tk     # from tkinter import Tk for Python 3.x
    from tkinter.filedialog import askopenfilename
except ImportError:
    install("tk")
    exit(1)

if 'VERY_IMPORTANT_FILE.txt' not in os.listdir():
    print('acquire the VERY_IMPORTANT_FILE.txt file from an admin, or someone that has it in general')
    print('and place it in the same directory as this script')
    input()
    exit()
with open('VERY_IMPORTANT_FILE.txt', 'r') as f:
    g = Github(f.read())

sel_repo = None
for repo in g.get_user().get_repos():
    if repo.name == "Lions-Roar-Site-Data":
        sel_repo = repo
git_file = 'data.json'
contents = sel_repo.get_contents(git_file)

with open('data.json', 'w') as f:
    data = json.loads(contents.decoded_content.decode())
    f.write(contents.decoded_content.decode())

# sort data by date
data = sorted(data, key=lambda k: k['year'] *
              1000000+k['month']*1000+k['day'], reverse=True)

abort = False

# modify data.json

months = ["January", "February", "March", "April", "May", "June",
          "July", "August", "September", "October", "November", "December"]

while True:
    options = ["Create new publication", "Edit existing publication",
               "Delete existing publication", "Attempt to recover deleted publication", "Create new extra", "Edit extra", "Relocate extra", "Delete extra", "Save and Exit", "Exit without saving"]
    option, index = pick.pick(
        options, "What would you like to do?", indicator='>', default_index=0)
    clear()
    if index == 0:
        suggested_date = datetime.date.today()
        if suggested_date.weekday() != 0:
            suggested_date = next_weekday(suggested_date, 0)
        year = suggested_date.year
        month = suggested_date.month
        title = input("Title: ")
        print("LEAVE BLANK TO KEEP SUGGESTION")
        year_p = input("Year ({}): ".format(year))
        if year_p != "":
            year = int(year_p)
        month_p = input("Month ({}): ".format(month))
        if month_p != "":
            month = int(month_p)
        day = suggested_date.day
        day_p = input("Day ({}): ".format(suggested_date.day))
        if day_p != "":
            day = int(day_p)
        week = week_of_month(date(year, month, day))

        url = input("URL: ")
        art_type = "link"
        if "youtube" in url:
            art_type = "video"
        elif "soundcloud" in url:
            art_type = "audio"
        elif "docs.google.com" in url:
            art_type = "text"
        elif "imgur" in url:
            art_type = "image"
        ind = art_types.index(art_type)
        art_type, ind = pick.pick(
            art_types, "What type of article is this?", indicator='>', default_index=ind)
        data.append({
            "year": year,
            "month": month,
            "week": week,
            "day": day,
            "main_article_title": title,
            "main_article_url": url,
            "main_article_thumbnail": None,
            "main_article_type": art_type,
            "release_timestamp": 0,
            "enabled": True,
            "articles": []
        })
    elif index == 1:
        pub_groups = [[]]
        for pub in data:
            if not pub["enabled"]:
                continue
            if len(pub_groups[-1]) >= 10:
                pub_groups.append([])
            pub_groups[-1].append(pub)
        pub_index = 0
        last_choice = "next"
        while True:
            options = []
            def_index = 0
            if pub_index != 0:
                options.append("Previous page")
            if pub_index != len(pub_groups)-1:
                options.append("Next page")
            if last_choice == "next":
                if "Next page" in options:
                    def_index = options.index("Next page")
                else:
                    def_index = 0
            if last_choice == "prev":
                if "Previous page" in options:
                    def_index = options.index("Previous page")
                else:
                    def_index = 0
            options.append("Cancel")
            for pub in pub_groups[pub_index]:
                options.append("Edit: {} ({} {})".format(
                    pub["main_article_title"], months[pub["month"]-1], pub["day"]))
            option, index = pick.pick(
                options, "", indicator='>', default_index=def_index)
            if option == "Cancel":
                break
            elif option == "Previous page":
                pub_index -= 1
                last_choice = "prev"
            elif option == "Next page":
                pub_index += 1
                last_choice = "next"
            else:
                if "Previous page" in options:
                    index -= 1
                if "Next page" in options:
                    index -= 1
                index -= 1
                pub = pub_groups[pub_index][index]
                break
        clear()
        print("Editing: {} ({} {})".format(
            pub["main_article_title"], months[pub["month"]-1], pub["day"]))
        print("LEAVE BLANK TO KEEP SUGGESTION")
        year_p = input("Year ({}): ".format(pub["year"]))
        if year_p != "":
            pub["year"] = int(year_p)
        month_p = input("Month ({}): ".format(pub["month"]))
        if month_p != "":
            pub["month"] = int(month_p)
        day_p = input("Day ({}): ".format(pub["day"]))
        if day_p != "":
            pub["day"] = int(day_p)
        week = week_of_month(date(pub["year"], pub["month"], pub["day"]))
        pub["week"] = week
        title_p = input("Title ({}): ".format(pub["main_article_title"]))
        if title_p != "":
            pub["main_article_title"] = title_p
        url_p = input("URL ({}): ".format(pub["main_article_url"]))
        if url_p != "":
            pub["main_article_url"] = url_p
        art_type = pub["main_article_type"]
        ind = art_types.index(art_type)
        art_type, ind = pick.pick(
            art_types, "What type of article is this?", indicator='>', default_index=ind)
        pub["main_article_type"] = art_type
    elif index == 2:
        pub_groups = [[]]
        for pub in data:
            if not pub["enabled"]:
                continue
            if len(pub_groups[-1]) >= 10:
                pub_groups.append([])
            pub_groups[-1].append(pub)
        pub_index = 0
        last_choice = "next"
        while True:
            options = []
            def_index = 0
            if pub_index != 0:
                options.append("Previous page")
            if pub_index != len(pub_groups)-1:
                options.append("Next page")
            if last_choice == "next":
                if "Next page" in options:
                    def_index = options.index("Next page")
                else:
                    def_index = 0
            if last_choice == "prev":
                if "Previous page" in options:
                    def_index = options.index("Previous page")
                else:
                    def_index = 0
            options.append("Cancel")
            for pub in pub_groups[pub_index]:
                options.append("Delete: {} ({} {})".format(
                    pub["main_article_title"], months[pub["month"]-1], pub["day"]))
            option, index = pick.pick(
                options, "", indicator='>', default_index=def_index)
            if option == "Cancel":
                break
            elif option == "Previous page":
                pub_index -= 1
                last_choice = "prev"
            elif option == "Next page":
                pub_index += 1
                last_choice = "next"
            else:
                if "Previous page" in options:
                    index -= 1
                if "Next page" in options:
                    index -= 1
                index -= 1
                pub = pub_groups[pub_index][index]
                options = ["Yes", "No"]
                option, index = pick.pick(options, 'Are you sure you want to delete "{}"?'.format(
                    pub["main_article_title"]), indicator='>', default_index=1)
                if option == "Yes":
                    pub["enabled"] = False
                    break
    elif index == 3:
        pub_groups = [[]]
        for pub in data:
            if pub["enabled"]:
                continue
            if len(pub_groups[-1]) >= 10:
                pub_groups.append([])
            pub_groups[-1].append(pub)
        pub_index = 0
        last_choice = "next"
        while True:
            options = []
            def_index = 0
            if pub_index != 0:
                options.append("Previous page")
            if pub_index != len(pub_groups)-1:
                options.append("Next page")
            if last_choice == "next":
                if "Next page" in options:
                    def_index = options.index("Next page")
                else:
                    def_index = 0
            if last_choice == "prev":
                if "Previous page" in options:
                    def_index = options.index("Previous page")
                else:
                    def_index = 0
            options.append("Cancel")
            for pub in pub_groups[pub_index]:
                options.append("Recover: {} ({} {})".format(
                    pub["main_article_title"], months[pub["month"]-1], pub["day"]))
            option, index = pick.pick(
                options, "", indicator='>', default_index=def_index)
            if option == "Cancel":
                break
            elif option == "Previous page":
                pub_index -= 1
                last_choice = "prev"
            elif option == "Next page":
                pub_index += 1
                last_choice = "next"
            else:
                if "Previous page" in options:
                    index -= 1
                if "Next page" in options:
                    index -= 1
                index -= 1
                pub = pub_groups[pub_index][index]
                options = ["Yes", "No"]
                option, index = pick.pick(options, 'Are you sure you want to attempt to recover "{}"?'.format(
                    pub["main_article_title"]), indicator='>', default_index=1)
                if option == "Yes":
                    bar = [
                        " [=     ]",
                        " [ =    ]",
                        " [  =   ]",
                        " [   =  ]",
                        " [    = ]",
                        " [     =]",
                        " [    = ]",
                        " [   =  ]",
                        " [  =   ]",
                        " [ =    ]",
                    ]
                    i = 0
                    print("Attempting to recover...")
                    for _ in range(50):
                        print(bar[i % len(bar)], end="\r")
                        time.sleep(.2)
                        i += 1
                    pub["enabled"] = True
                    break
    elif index == 4:
        pub_groups = [[]]
        for pub in data:
            if not pub["enabled"]:
                continue
            if len(pub_groups[-1]) >= 10:
                pub_groups.append([])
            pub_groups[-1].append(pub)
        pub_index = 0
        last_choice = "next"
        while True:
            options = []
            def_index = 0
            if pub_index != 0:
                options.append("Previous page")
            if pub_index != len(pub_groups)-1:
                options.append("Next page")
            if last_choice == "next":
                if "Next page" in options:
                    def_index = options.index("Next page")
                else:
                    def_index = 0
            if last_choice == "prev":
                if "Previous page" in options:
                    def_index = options.index("Previous page")
                else:
                    def_index = 0
            options.append("Cancel")
            for pub in pub_groups[pub_index]:
                options.append("Attach extra: {} ({} {})".format(
                    pub["main_article_title"], months[pub["month"]-1], pub["day"]))
            option, index = pick.pick(
                options, "", indicator='>', default_index=def_index)
            pub = None
            if option == "Cancel":
                break
            elif option == "Previous page":
                pub_index -= 1
                last_choice = "prev"
            elif option == "Next page":
                pub_index += 1
                last_choice = "next"
            else:
                if "Previous page" in options:
                    index -= 1
                if "Next page" in options:
                    index -= 1
                index -= 1
                pub = pub_groups[pub_index][index]
                break
        clear()
        if pub == None:
            continue
        print("Selected: {} ({} {})".format(
            pub["main_article_title"], months[pub["month"]-1], pub["day"]))
        print("Creating new extra")
        title = input("Title of extra: ")
        Tk().withdraw()  # we don't want a full GUI, so keep the root window from appearing
        # show an "Open" dialog box and return the path to the selected file
        print("Please enter the day this extra was produced")
        month = int(input("Month (1-12): "))
        day = int(input("Day (1-31): "))
        url = input("URL to redirect to: ")
        art_type = "link"
        if "youtube" in url:
            art_type = "video"
        elif "soundcloud" in url:
            art_type = "audio"
        elif "docs.google.com" in url:
            art_type = "text"
        elif "imgur" in url:
            art_type = "image"
        ind = art_types.index(art_type)
        art_type, ind = pick.pick(
            art_types, "What type of article is this?", indicator='>', default_index=ind)
        options = ["Yes", "No"]
        option, index = pick.pick(
            options, 'Do you want to add a custom thumbnail?', indicator='>', default_index=1)
        if option == "Yes":
            filename = askopenfilename(title="Select thumbnail file")
            if filename == "":
                repofile = None
            else:
                repofile = "thumbnails/" + \
                    str(time.time())+"."+filename.split(".")[-1]
        else:
            repofile = None
        author = input("Author: ")
        if repofile != None:
            with open(filename, 'rb') as f:
                repo.create_file(repofile, "upload thumbnail", f.read())
        tags_enabled = [False]*len(tags_types)
        index = 0
        while True:
            options = []
            for i in range(len(tags_types)):
                if tags_enabled[i]:
                    options.append("[#] "+tags_types[i])
                else:
                    options.append("[ ] "+tags_types[i])
            options.append("Done")
            option, index = pick.pick(
                options, "Select the extra's tags", indicator='>', default_index=index)
            if option == "Done":
                break
            else:
                tags_enabled[index] = not tags_enabled[index]
        tags = []
        for i in range(len(tags_types)):
            if tags_enabled[i]:
                tags.append(tags_types[i])
        if repofile == None:
            thumbnail = None
        else:
            thumbnail = "https://raw.githubusercontent.com/2canupea/Lions-Roar-Site-Data/main/"+repofile
        pub["articles"].append({
            "title": title,
            "author": author,
            "date": str(day)+" "+months[month-1],
            "url": url,
            "type": art_type,
            "thumbnail": thumbnail,
            "tags": tags
        })
    elif index == 5:
        pub_groups = [[]]
        for pub in data:
            if not pub["enabled"]:
                continue
            if len(pub_groups[-1]) >= 10:
                pub_groups.append([])
            pub_groups[-1].append(pub)
        pub_index = 0
        last_choice = "next"
        while True:
            options = []
            def_index = 0
            if pub_index != 0:
                options.append("Previous page")
            if pub_index != len(pub_groups)-1:
                options.append("Next page")
            if last_choice == "next":
                if "Next page" in options:
                    def_index = options.index("Next page")
                else:
                    def_index = 0
            if last_choice == "prev":
                if "Previous page" in options:
                    def_index = options.index("Previous page")
                else:
                    def_index = 0
            options.append("Cancel")
            for pub in pub_groups[pub_index]:
                options.append("Edit extras: {} ({} {})".format(
                    pub["main_article_title"], months[pub["month"]-1], pub["day"]))
            option, index = pick.pick(
                options, "", indicator='>', default_index=def_index)
            pub = None
            if option == "Cancel":
                break
            elif option == "Previous page":
                pub_index -= 1
                last_choice = "prev"
            elif option == "Next page":
                pub_index += 1
                last_choice = "next"
            else:
                if "Previous page" in options:
                    index -= 1
                if "Next page" in options:
                    index -= 1
                index -= 1
                pub = pub_groups[pub_index][index]
                break
        clear()
        if pub == None:
            continue
        extra_groups = [[]]
        for extra in pub["articles"]:
            if len(extra_groups[-1]) >= 10:
                extra_groups.append([])
            extra_groups[-1].append(extra)
        extra_index = 0
        last_choice = "next"
        while True:
            options = []
            def_index = 0
            if extra_index != 0:
                options.append("Previous page")
            if extra_index != len(extra_groups)-1:
                options.append("Next page")
            if last_choice == "next":
                if "Next page" in options:
                    def_index = options.index("Next page")
                else:
                    def_index = 0
            if last_choice == "prev":
                if "Previous page" in options:
                    def_index = options.index("Previous page")
                else:
                    def_index = 0
            options.append("Cancel")
            for extra in extra_groups[extra_index]:
                options.append("Edit: {}".format(extra["title"]))
            option, index = pick.pick(
                options, "", indicator='>', default_index=def_index)
            extra = None
            if option == "Cancel":
                break
            elif option == "Previous page":
                extra_index -= 1
                last_choice = "prev"
            elif option == "Next page":
                extra_index += 1
                last_choice = "next"
            else:
                if "Previous page" in options:
                    index -= 1
                if "Next page" in options:
                    index -= 1
                index -= 1
                extra = extra_groups[extra_index][index]
                break
        clear()
        if extra == None:
            continue
        print("PRESS ENTER TO KEEP ORIGINAL VALUE")
        title = input("Title ({}): ".format(extra["title"]))
        if title == "":
            title = extra["title"]
        option, index = pick.pick(["Yes", "No"], ("Do you want to change the date? ({})".format(
            extra["date"])), indicator='>', default_index=1)
        if option == "Yes":
            day = int(input("Day: "))
            month = int(input("Month: "))
            date = str(day)+" "+months[month-1]
        else:
            date = extra["date"]
        url = input("URL ({}): ".format(extra["url"]))
        if url == "":
            url = extra["url"]
        art_type = extra["type"]
        ind = art_types.index(art_type)
        art_type, ind = pick.pick(
            art_types, "What type of article is this?", indicator='>', default_index=ind)
        option, index = pick.pick(
            ["Yes", "No"], "Do you want to change the thumbnail?", indicator='>', default_index=1)
        if option == "Yes":
            filename = askopenfilename(title="Select thumbnail file")
            if filename == "":
                repofile = None
            else:
                repofile = "thumbnails/" + \
                    str(time.time())+"."+filename.split(".")[-1]
        else:
            repofile = 0
        author = input("Author ({}): ".format(extra["author"]))
        if author == "":
            author = extra["author"]
        tags_enabled = [False]*len(tags_types)
        for tag in extra["tags"]:
            tags_enabled[tags_types.index(tag)] = True
        index = 0
        while True:
            options = []
            for i in range(len(tags_types)):
                if tags_enabled[i]:
                    options.append("[#] "+tags_types[i])
                else:
                    options.append("[ ] "+tags_types[i])
            options.append("Done")
            option, index = pick.pick(
                options, "Select the extra's tags", indicator='>', default_index=index)
            if option == "Done":
                break
            else:
                tags_enabled[index] = not tags_enabled[index]
        tags = []
        for i in range(len(tags_types)):
            if tags_enabled[i]:
                tags.append(tags_types[i])
        extra["type"] = art_type
        extra["title"] = title
        extra["date"] = date
        extra["url"] = url
        extra["author"] = author
        extra["tags"] = tags
        if repofile != None and repofile != 0:
            with open(filename, 'rb') as f:
                repo.create_file(repofile, "upload thumbnail", f.read())
        if repofile != 0:
            if repofile == None:
                thumbnail = None
            else:
                thumbnail = "https://raw.githubusercontent.com/2canupea/Lions-Roar-Site-Data/main/"+repofile
            extra["thumbnail"] = thumbnail
    elif index == 6:
        pub_groups = [[]]
        for pub in data:
            if not pub["enabled"]:
                continue
            if len(pub_groups[-1]) >= 10:
                pub_groups.append([])
            pub_groups[-1].append(pub)
        pub_index = 0
        last_choice = "next"
        while True:
            options = []
            def_index = 0
            if pub_index != 0:
                options.append("Previous page")
            if pub_index != len(pub_groups)-1:
                options.append("Next page")
            if last_choice == "next":
                if "Next page" in options:
                    def_index = options.index("Next page")
                else:
                    def_index = 0
            if last_choice == "prev":
                if "Previous page" in options:
                    def_index = options.index("Previous page")
                else:
                    def_index = 0
            options.append("Cancel")
            for pub in pub_groups[pub_index]:
                options.append("Move extras: {} ({} {})".format(
                    pub["main_article_title"], months[pub["month"]-1], pub["day"]))
            option, index = pick.pick(
                options, "", indicator='>', default_index=def_index)
            pub = None
            if option == "Cancel":
                break
            elif option == "Previous page":
                pub_index -= 1
                last_choice = "prev"
            elif option == "Next page":
                pub_index += 1
                last_choice = "next"
            else:
                if "Previous page" in options:
                    index -= 1
                if "Next page" in options:
                    index -= 1
                index -= 1
                pub = pub_groups[pub_index][index]
                break
        clear()
        if pub == None:
            continue
        pub1 = pub
        extra_groups = [[]]
        for extra in pub["articles"]:
            if len(extra_groups[-1]) >= 10:
                extra_groups.append([])
            extra_groups[-1].append(extra)
        extra_index = 0
        last_choice = "next"
        while True:
            options = []
            def_index = 0
            if extra_index != 0:
                options.append("Previous page")
            if extra_index != len(extra_groups)-1:
                options.append("Next page")
            if last_choice == "next":
                if "Next page" in options:
                    def_index = options.index("Next page")
                else:
                    def_index = 0
            if last_choice == "prev":
                if "Previous page" in options:
                    def_index = options.index("Previous page")
                else:
                    def_index = 0
            options.append("Cancel")
            for extra in extra_groups[extra_index]:
                options.append("Move: {}".format(extra["title"]))
            option, index = pick.pick(
                options, "", indicator='>', default_index=def_index)
            extra = None
            if option == "Cancel":
                break
            elif option == "Previous page":
                extra_index -= 1
                last_choice = "prev"
            elif option == "Next page":
                extra_index += 1
                last_choice = "next"
            else:
                if "Previous page" in options:
                    index -= 1
                if "Next page" in options:
                    index -= 1
                index -= 1
                extra = extra_groups[extra_index][index]
                break
        clear()
        if extra == None:
            continue
        pub_groups = [[]]
        for pub in data:
            if not pub["enabled"]:
                continue
            if len(pub_groups[-1]) >= 10:
                pub_groups.append([])
            pub_groups[-1].append(pub)
        pub_index = 0
        last_choice = "next"
        while True:
            options = []
            def_index = 0
            if pub_index != 0:
                options.append("Previous page")
            if pub_index != len(pub_groups)-1:
                options.append("Next page")
            if last_choice == "next":
                if "Next page" in options:
                    def_index = options.index("Next page")
                else:
                    def_index = 0
            if last_choice == "prev":
                if "Previous page" in options:
                    def_index = options.index("Previous page")
                else:
                    def_index = 0
            options.append("Cancel")
            for pub in pub_groups[pub_index]:
                options.append("Move extras: {} ({} {})".format(
                    pub["main_article_title"], months[pub["month"]-1], pub["day"]))
            option, index = pick.pick(
                options, "", indicator='>', default_index=def_index)
            pub = None
            if option == "Cancel":
                break
            elif option == "Previous page":
                pub_index -= 1
                last_choice = "prev"
            elif option == "Next page":
                pub_index += 1
                last_choice = "next"
            else:
                if "Previous page" in options:
                    index -= 1
                if "Next page" in options:
                    index -= 1
                index -= 1
                pub = pub_groups[pub_index][index]
                break
        clear()
        if pub == None:
            continue
        pub2 = pub
        pub2["articles"].append(extra)
        pub1["articles"].remove(extra)
    elif index == 7:
        pub_groups = [[]]
        for pub in data:
            if not pub["enabled"]:
                continue
            if len(pub_groups[-1]) >= 10:
                pub_groups.append([])
            pub_groups[-1].append(pub)
        pub_index = 0
        last_choice = "next"
        while True:
            options = []
            def_index = 0
            if pub_index != 0:
                options.append("Previous page")
            if pub_index != len(pub_groups)-1:
                options.append("Next page")
            if last_choice == "next":
                if "Next page" in options:
                    def_index = options.index("Next page")
                else:
                    def_index = 0
            if last_choice == "prev":
                if "Previous page" in options:
                    def_index = options.index("Previous page")
                else:
                    def_index = 0
            options.append("Cancel")
            for pub in pub_groups[pub_index]:
                options.append("Delete extras: {} ({} {})".format(
                    pub["main_article_title"], months[pub["month"]-1], pub["day"]))
            option, index = pick.pick(
                options, "", indicator='>', default_index=def_index)
            pub = None
            if option == "Cancel":
                break
            elif option == "Previous page":
                pub_index -= 1
                last_choice = "prev"
            elif option == "Next page":
                pub_index += 1
                last_choice = "next"
            else:
                if "Previous page" in options:
                    index -= 1
                if "Next page" in options:
                    index -= 1
                index -= 1
                pub = pub_groups[pub_index][index]
                break
        clear()
        if pub == None:
            continue
        extra_groups = [[]]
        for extra in pub["articles"]:
            if len(extra_groups[-1]) >= 10:
                extra_groups.append([])
            extra_groups[-1].append(extra)
        extra_index = 0
        last_choice = "next"
        while True:
            options = []
            def_index = 0
            if extra_index != 0:
                options.append("Previous page")
            if extra_index != len(extra_groups)-1:
                options.append("Next page")
            if last_choice == "next":
                if "Next page" in options:
                    def_index = options.index("Next page")
                else:
                    def_index = 0
            if last_choice == "prev":
                if "Previous page" in options:
                    def_index = options.index("Previous page")
                else:
                    def_index = 0
            options.append("Cancel")
            for extra in extra_groups[extra_index]:
                options.append("Delete: {}".format(extra["title"]))
            option, index = pick.pick(
                options, "", indicator='>', default_index=def_index)
            extra = None
            if option == "Cancel":
                break
            elif option == "Previous page":
                extra_index -= 1
                last_choice = "prev"
            elif option == "Next page":
                extra_index += 1
                last_choice = "next"
            else:
                if "Previous page" in options:
                    index -= 1
                if "Next page" in options:
                    index -= 1
                index -= 1
                extra = extra_groups[extra_index][index]
                break
        clear()
        if extra == None:
            continue
        pub["articles"].remove(extra)

    elif index == 8:
        break
    elif index == 9:
        abort = True
        break

# update data.json
if abort:
    exit(0)
with open('data.json', 'w') as f:
    f.write(json.dumps(data))
sel_repo.update_file(contents.path, "updating data",
                     json.dumps(data, indent=4), contents.sha)
