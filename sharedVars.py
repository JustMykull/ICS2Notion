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

        # print(EVENTS)

