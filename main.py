import scratchattach as scratch3 
from scratchattach import Encoding  
from datetime import datetime
import wikipediaapi 
import os 
import re
import tkinter as tk
from tkinter import ttk

# Scratch connection
with open("logs/info.txt", "r") as file:
    data = file.readlines()
    id = data[0]
    session = scratch3.login(data[1], data[2])
    conn = scratch3.CloudConnection(
        project_id=id,
        username=data[1],
        session_id=data[3]
    )
events = scratch3.CloudEvents(id)
stored_operation = {"last_online": "", "response": ""}
operation = ""
operation_response = {
    "change" : "",
    "username" : "", 
    "days-since-2000": "", #return days since 2000
    "error" : "" # return any error code...
}

# Tkinter
root = tk.Tkinter()
root.mainloop()

def main():
    global events
    if not os.path.exists("logs/"): # Create text files if they don't exist in folder logs/
        os.makedirs("logs/")
        f = open("logs/info.txt", "w+")
        f.close()
        f = open("logs/query.txt", "w+")
        f.close() 
        f = open("logs/updates.txt", "w+")
        f.close() 
        f = open("logs/users.txt", "w+")
        f.close()  
    if scratch3.get_var(id, "operation") is not None:
        setup_tkinter()
        print("Successfully initialized.\nStarting event listener...")
        events.start(thread=True)
    else:
        print(scratch3.get_cloud(id))
        print(scratch3.get_var(id, "username"))
        print("Failed to connect properly. Exiting...")

    

def wiki(query):
    q = query
    wiki_wiki = wikipediaapi.Wikipedia(
        "Scratch Wikipedia (https://scratch.mit.edu/projects/1059644681/) (Contact: yamcrunchy@gmail.com)",
        "en",
    )
    page_py = wiki_wiki.page(q)
    if page_py.exists():
        print("Page exists")
    else:
        print("Page does not exist.")


def decode(val):
    if val is not None:
        return Encoding.decode(val)
    else:
        return "Error 400: Bad request"


def encode(val):
    if val is not None:
        return Encoding.encode(val)
    else:
        return "Error 400: Bad request"


def decode_list(query):
    q = Encoding.decode(query)
    result = []
    p = 0
    i = 0
    while p < len(q):
        result.append("")
        while q[p] != "|":
            result[i] = result[i] + q[p]
            p += 1
        i += 1
        p += 1

    return result


def encode_list(query):
    q = list(query)
    result = ""
    for x in range(len(q)):
        result = result + q[x] + "|"
    return encode(result)


def log(string, location):
    f = open("logs/" + location + ".txt", "a")
    f.write(string)
    f.close()

def get_vars(): # Fetch, declare and store cloud variables
    global operation
    operation = scratch3.get_var(id, "operation")

def fragment(query): # Split up a long message into smaller packets (max 256 length per cloud variable (8 unused)). 
    if len(query) > 256:
        pass
    else:
        return query

def user_in_users(username):
    with open("logs/users.txt", "r") as file:
        file = file.read()
        match = re.search(username, file)
        return match is not None

def handle_operation(event):
    if event.var == "operation":
        d_operation = decode_list(operation)  # decoded values necessary to operate
        print(d_operation[0])
        operation_vars = {
            "change" : d_operation[0],
            "username" : d_operation[1],
            "days-since-2000" : d_operation[2],
            "time" : d_operation[3],
            "type" : d_operation[4],
            "request" : d_operation[5]
       }
        if operation_vars["type"] == "update":
            if not user_in_users(operation_vars["username"]):
                log(operation_vars["username"] + "\n", "users")
                print("User " + operation_vars["username"] + " logged to log/users.txt")
                msg = f"User {operation_vars['username']} + was added to database!"
            else:
                msg = "Welcome back " + operation_vars["username"]

            operation_response = {
                "change" : operation_vars["change"],
                "username" : "Resource accessed by " + operation_vars["username"],
                "days-since-2000" : operation_vars['days-since-2000'],
                "msg" : msg,
                "error" : "Status 200 OK",
            }
            conn.set_var("operation_response", encode_list(operation_response.values()))

            log(f"Operation Status Updated @ {operation_vars['time']} by user {operation_vars['username']}\n", "updates")
            print(f"Operation Status Updated @ {operation_vars['time']} by user {operation_vars['username']}\n")


def handle_wiki(event):
    if event.var == "wiki_request":
        print("a ok")


@events.event
def on_set(event):
    get_vars()
    handle_operation(event)
    handle_wiki(event)

if __name__ == "__main__":
    main()
