from configparser import ConfigParser

#keeps all the auth tokens and stuff on one file
config = ConfigParser()
config.read("configs.ini")

def getConfig(configRequest : str):
    if configRequest == "ICS_URL":
        return config["AUTH"]["ICS_URL"]
    
    elif configRequest == "NOTIONTOKEN":
        return config["AUTH"]["NOTIONTOKEN"]

    elif configRequest == "DATABASEID":
        return config["AUTH"]["DATABASEID"]
    
    elif configRequest == "DISCORDBOT_TOKEN":
        return config["DISCORD"]["DISCORDBOT_TOKEN"]
    
    elif configRequest == "TIMEZONE":
        return config["TIMEZONE"]["TIMEZONE"]

ASSIGNEMTNAMES = []
COURSECODE = []
DEADLINE = []
EVENTID = []

ExistingEventID = []
ExistingAssignmentNames = []

EVENTS = []

 #Format the events so that they are in dictionary form in a list.
def formatEvents():
    for id in EVENTID:
        EVENTS.append({
            "Assignment Name" : ASSIGNEMTNAMES.pop(0),
            "Course Code" : COURSECODE.pop(0),
            "Deadline" : DEADLINE.pop(0),
            "EventID" : id
        })