import scratchattach as scratch3
from scratchattach import Encoding
from datetime import datetime
import wikipediaapi
import os
import re
import tkinter as tk
import sys
from better_profanity import profanity

# Scratch connection
username = os.environ["username"]
password = os.environ["password"]
project_id = os.environ["project_id"]
session_id = os.environ["session_id"]
session = scratch3.login(username, password)
conn = scratch3.CloudConnection(
    project_id=project_id,
    username=username,
    session_id=session_id
)

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
status = "Free"
wiki_index = 0
wiki_response = ""
wiki_chunkcount = 0
wiki_request = ""
# Tkinter
class Window: # GUI (Window, label, kill and pause button)
    def __init__(self):
        self.root = tk.Tk()

        self.root.geometry("500x500")
        self.root.configure(background='white')
        self.title = tk.Label(self.root, text="Scratchpedia GUI", font=("Arial", 20), background="white")
        self.title.pack(pady=5)

        self.buttonframe = tk.Frame(self.root)
        self.buttonframe.columnconfigure(0, weight=1)

        self.killBtn = tk.Button(
            self.root, text="Kill program", font=("Arial", 14), command=self.kill, background="white"
        )
        self.killBtn.pack(padx=5, pady=5)

        self.pauseBtn = tk.Button(
            self.root, text="Pause", font=("Arial", 8), command=self.pause, background="white"
        )
        self.pauseBtn.pack(padx=5, pady=10)
        self.root.mainloop()

    def kill(self): # Ends program
        self.root.destroy()
        events.stop()
        sys.exit("Program killed.")

    def pause(self):
        if self.pauseBtn.cget("text") == "Pause":
            self.pauseBtn.config(text="Unpause")
            events.stop()
            print("Event listenting stopped.")
        else: # Unpause doesn't work 
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
        f = open("logs/info.txt", "a")
        f.write("# Paste project id here\n# Enter Scratch username here\n# Enter Scratch password here\n # Enter Scratch SessionID here")
        f = open("logs/query.txt", "w+")
        f.close()
        f = open("logs/updates.txt", "w+")
        f.close()
        f = open("logs/users.txt", "w+")
        f.close()
        f = open("logs/profanity.txt", "w+")
        f.close()
        f = open("logs/wiki.txt", "w+")
        f.close()
    words = ["genital", "genitals", "herpes", "sex", "sexual", "syphilis", "gonorrhoea", "chlamydia", "trichomoniasis", "hepatitis", "HIV", "papillomavirus", "HPV", "GTA", "circumcision", "slurs", "slur", "racist"]
    profanity.add_censor_words(words)
    if scratch3.get_var(id, "operation") is not None:
        print("Successfully initialized.\nStarting event listener...")
        events.start(thread=True)
        Window()
    else:
        print(scratch3.get_cloud(id))
        print(scratch3.get_var(id, "username"))
        print("Failed to connect properly. Exiting...")


def clear_txt(location):
    f = open(location, "r+")
    f.seek(0)
    f.truncate()

def wiki(query, type): # Handle wiki requests
    wiki_wiki = wikipediaapi.Wikipedia(
        "Scratch Wikipedia (https://scratch.mit.edu/projects/1059644681/) (Contact: yamcrunchy@gmail.com)",
        "en",
    )
    page_py = wiki_wiki.page(query) # Query page
    wiki_response = {
        "title": page_py.title,
        "content": str(page_py.summary[0:len(str(page_py.summary))]).replace("\n", " ")
        }
    if page_py.exists(): # If page exists continue
        if type == "title":
            return page_py.title
        elif type == "content": # Return content chunks
            encoded_wiki_response = encode(wiki_response["content"])
            chunks = [encoded_wiki_response[i:i + 256] for i in range(0, len(encoded_wiki_response), 256)]
            return(chunks)
        elif type == "exists":
            return True
    else: # If page does not exist
        return False


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
    temp = ""
    
    for char in q:
        if char == "|":
            result.append(temp)
            temp = ""
        else:
            temp += char

    return result



def encode_list(query):
    if query is None:
        return "Error: None"
    
    result = "|".join(list(query)) + "|"
    return Encoding.encode(result)



def log(string, location):
    f = open("logs/" + location + ".txt", "a")
    f.write(string)
    f.close()


def get_vars():  # Fetch, declare and store cloud variables
    global operation
    operation = scratch3.get_var(id, "operation")

def user_in_users(username):
    with open("logs/users.txt", "r") as file:
        file = file.read()
        match = re.search(username, file)
        return match is not None


def handle_operation(event):
    global change, status, wiki_index, wiki_response, wiki_chunkcount, wiki_request

    if event.var == "operation":
        
        d_operation = decode_list(scratch3.get_var(id, "operation"))  
        operation_vars = { # Decoded cloud variable operation packet
            "change": d_operation[0],
            "username": d_operation[1],
            "days-since-2000": d_operation[2],
            "time": d_operation[3],
            "type": d_operation[4],
            "request": d_operation[5],
            "chunk-number": d_operation[6]
        }
        if not user_in_users(operation_vars["username"]): # Check if user has used project prior
            log(operation_vars["username"] + "\n", "users") # Add username to logs/users.txt
            with open("logs/users.txt", "r") as file:
                user_num = len(file.readlines())
            print(f"User {operation_vars["username"]} logged to log/users.txt (# {user_num})") 
            msg = f"{operation_vars['username']} has been added as the {user_num}th user to users text file."
        else: # User has used before
            msg = "Welcome back " + operation_vars["username"]

        if operation_vars["type"] == "update" and operation_vars["change"] != change: # Respond to ping
            status = "Responding to ping request"

            operation_response = { # Operation Response packet
                "change": operation_vars["change"],
                "username": operation_vars["username"],
                "days-since-2000": operation_vars["days-since-2000"],
                "msg": msg,
                "error": "Status 200 OK",
            }
            change = operation_vars["change"] # Update local change
            conn.set_var("operation_response", encode_list(operation_response.values())) # Send packet

            log( # Record ping
                f"{operation_vars["change"]} Operation Status Updated @ {operation_vars['time']} by user {operation_vars['username']}\n",
                "updates",
            ) 
            print(
                f"{operation_vars["change"]} Operation Status Updated @ {operation_vars['time']} by user {operation_vars['username']}\n"
            )
            status = "free"

        elif operation_vars["type"] == "request" and operation_vars["change"] != change: # If request is for wiki access
            status = "responding to wiki access request"
            log(f"{operation_vars['change']} Received Request @ {operation_vars['time']} from user {operation_vars['username']} \n", "updates")
            print(f"{operation_vars['change']} Received Request @ {operation_vars['time']} from user {operation_vars['username']}")
            change = operation_vars["change"]
            profanity.load_censor_words()
            if profanity.contains_profanity(operation_vars['request']): # If request was profane log and restrict
                status = "responding to denied wiki access"
                msg = "Request denied: Profanity. User recorded!"
                operation_response = {
                    "change": change,
                    "username": operation_vars["username"],
                    "days-since-2000": operation_vars["days-since-2000"],
                    "msg": msg,
                    "error": "Error 400: Bad request",
                } 
                log(f'{change} Profanity: "{operation_vars["request"]}" @{operation_vars["time"]} by user {operation_vars["username"]}\n', "profanity") # Log username and request
                conn.set_var("operation_response", encode_list(operation_response.values())) # Return operation response
                status = "free"
            else:
                if not wiki(operation_vars["request"], "exists") == False: # Check if wiki page exists
                    status = "wiki-busy"
                    wiki_index = 0
                    wiki_response = wiki(operation_vars["request"], "content") # Store encoded 256char length wiki summary into variable
                    wiki_chunkcount = len(wiki_response) - 1
                    wiki_request = operation_vars["request"]
                    msg = "Request accepted. Please wait..."
                    operation_response = {
                        "change": change,
                        "username": operation_vars["username"],
                        "days-since-2000": operation_vars["days-since-2000"],
                        "msg": msg,
                        "error": "Status 202 OK",
                        "title": wiki(operation_vars["request"], "title"),
                        "length": str(len(wiki_response))
                    }
                    conn.set_var("operation_response", encode_list(operation_response.values())) 
                    conn.set_var("content", wiki_response[wiki_index])
                    conn.set_var("index", "0")
                    log(f'{operation_vars["change"]} "{operation_vars["request"]}" pulled from wiki @ {operation_vars["time"]} by user {operation_vars["username"]}\n', "query")
                    
        elif operation_vars["type"] == "wiki-update" and status == "wiki-busy":
            print(f"{operation_vars['change']} Recieved permission to continue to next chunk. @ {operation_vars['time']} from user {operation_vars['username']}")
            if wiki_chunkcount <= wiki_index:
                status = "free"
                wiki_index = 0
                log_msg = f'{operation_vars["change"]} Finished query "{wiki_request}" @ {operation_vars["time"]} from {operation_vars["username"]}'
                log(log_msg + "\n", "updates")
                print(log_msg)
            else: 
                wiki_index+=1
                conn.set_var("content", wiki_response[wiki_index])

        else:
            status = "Invalid request"
            msg = "ERROR: Invalid request. Please try again."
            operation_response = {
                "change": operation_vars["change"],
                "username": operation_vars["username"],
                "days-since-2000": operation_vars["days-since-2000"],
                "msg": msg,
                "error": "Error 400: Bad request"
            }
            conn.set_var("operation_response", encode_list(operation_response.values()))
            status = "free"


@events.event
def on_set(event):
    get_vars()
    handle_operation(event)

if __name__ == "__main__":
    main()
