from notion_client import Client
import json
import sharedVars

client = Client(auth=sharedVars.getConfig("NOTIONTOKEN"))
dbID = sharedVars.getConfig("DATABASEID")

file_path = "pages.json"


def jsonDump(pages):
    try:
        with open(file_path, "w") as json_file:
            json.dump(pages, json_file, indent=4)
    except Exception as error:
        print(error)


def getAssignments(databaseID):
    try:
        pages = []
        query = client.databases.query(database_id=databaseID)
        pages.extend(query["results"])

        while query.get("has_more", False):
            query = client.databases.query(
                database_id=databaseID,
                start_cursor=query["next_cursor"]
            )
            pages.extend(query["results"])

        jsonDump(pages)
        return pages

    except Exception as error:
        print(error)


def createAssignment(databaseID, assignmentName, courseCode, Deadline, EventID):
    try:
        return client.pages.create(
            parent={"database_id": databaseID},
            properties={
                "Assignment Name": {
                    "title": [{"text": {"content": assignmentName}}]
                },
                "Course Code": {
                    "select": {"name": courseCode}
                },
                "Deadline": {
                    "date": {"start": Deadline}
                },
                "EventID": {
                    "rich_text": [{
                        "text": {"content": EventID or "MISSING_ID"}
                    }]
                }
            }
        )
    except Exception as error:
        print(error, "NotionAPI Page")
