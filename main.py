import scratchattach as scratch3
from scratchattach import Encoding
from datetime import datetime
import wikipediaapi
import os
import re
import tkinter as tk
import sys

# Scratch connection
with open("logs/info.txt", "r") as file:  # Get sensitive information
    data = file.readlines()
    id = data[0].replace("\n", "")
    session = scratch3.login(data[1].replace("\n", ""), data[2].replace("\n", ""))
    conn = scratch3.CloudConnection(
        project_id=id,
        username=data[1].replace("\n", ""),
        session_id=data[3].replace("\n", ""),
    )
events = scratch3.CloudEvents(id)
stored_operation = {"last_online": "", "response": ""}
operation = ""
operation_response = {
    "change": "",
    "username": "",
    "days-since-2000": "",  # return days since 2000
    "error": "",  # return any error code...
}
change = ""


# Tkinter
class Window:
    def __init__(self):
        self.root = tk.Tk()

        self.root.geometry("500x500")

        self.title = tk.Label(self.root, text="Scratchpedia", font=("Arial", 20))
        self.title.pack(pady=5)

        self.buttonframe = tk.Frame(self.root)

        self.buttonframe.columnconfigure(0, weight=1)

        self.killBtn = tk.Button(
            self.root, text="Kill program", font=("Arial", 14), command=self.kill
        )
        self.killBtn.pack(padx=5, pady=5)

        self.pauseBtn = tk.Button(
            self.root, text="Pause", font={"Arial", 8}, command=self.pause
        )
        self.pauseBtn.pack(padx=5, pady=10)
        self.root.mainloop()

    def kill(self):
        self.root.destroy()
        events.stop()
        sys.exit("Program killed.")

    def pause(self):
        if self.pauseBtn.cget("text") == "Pause":
            self.pauseBtn.config(text="Unpause")
            events.stop()
            print("Event listenting stopped.")
        else:
            self.pauseBtn.config(text="Pause")
            events.start(thread=True)
            print("Event listener now listening.")


def main():
    global events
    if not os.path.exists(
        "logs/"
    ):  # Create text files if they don't exist in folder logs/
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
        print("Successfully initialized.\nStarting event listener...")
        events.start(thread=True)
        Window()
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


def get_vars():  # Fetch, declare and store cloud variables
    global operation
    operation = scratch3.get_var(id, "operation")


def fragment(
    query,
):  # Split up a long message into smaller packets (max 256 length per cloud variable (8 unused)).
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
    global change
    if event.var == "operation":
        d_operation = decode_list(operation)  # decoded values necessary to operate
        operation_vars = {
            "change": d_operation[0],
            "username": d_operation[1],
            "days-since-2000": d_operation[2],
            "time": d_operation[3],
            "type": d_operation[4],
            "request": d_operation[5],
        }
        if operation_vars["type"] == "update" and operation_vars["change"] != change:
            if not user_in_users(operation_vars["username"]):
                log(operation_vars["username"] + "\n", "users")
                print("User " + operation_vars["username"] + " logged to log/users.txt")
                msg = f"User {operation_vars['username']} + was added to database!"
            else:
                msg = "Welcome back " + operation_vars["username"]

            operation_response = {
                "change": operation_vars["change"],
                "username": "Resource accessed by " + operation_vars["username"],
                "days-since-2000": operation_vars["days-since-2000"],
                "msg": msg,
                "error": "Status 200 OK",
            }
            change = operation_vars["change"]
            conn.set_var("operation_response", encode_list(operation_response.values()))

            log(
                f"{operation_vars["change"]} Operation Status Updated @ {operation_vars['time']} by user {operation_vars['username']}\n",
                "updates",
            )
            print(
                f"{operation_vars["change"]} Operation Status Updated @ {operation_vars['time']} by user {operation_vars['username']}\n"
            )

        elif operation_vars["type"] == "request" and operation_vars["change"] != change:
            print("recieved request")
            change = operation_vars["change"]
            msg = "hello"
            operation_response = {
                "change": change,
                "username": "Resource accessed by " + operation_vars["username"],
                "days-since-2000": operation_vars["days-since-2000"],
                "msg": msg,
                "error": "Status 200 OK",
            }
            conn.set_var("operation_response", encode_list(operation_response.values()))
        else:
            msg = "ERROR"
            operation_response = {
                "change": operation_vars["change"],
                "username": "Resource accessed by " + operation_vars["username"],
                "days-since-2000": operation_vars["days-since-2000"],
                "msg": msg,
                "error": "Error 400: Bad request",
            }
            conn.set_var("operation_response", encode_list(operation_response.values()))



@events.event
def on_set(event):
    get_vars()
    handle_operation(event)


if __name__ == "__main__":
    main()
