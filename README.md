# SCRATCHPEDIA

# Overview

Scratchpedia is a Python program that uses scratchattach and wikipedia-api to send and recieve information between wikipedia articles and the scratch project, all relayed through the computer running it.

# Installation

Get the latest version of Python3 [Here](https://www.python.org/downloads/)<br>
To install this project paste the following into your bash terminal:

```
git clone https://github.com/yamcrunchy/scratchpedia.git
```

Then proceed to remix this scratch project: https://scratch.mit.edu/projects/1059644681

<br> Be sure to install all dependencies in requirements.txt through pip<br>
They are as follows: (It is assumed you already have pip and python3)

- scratchattach [Here](https://github.com/TimMcCool/scratchattach/)
- Wikipedia-api [Here](https://github.com/martin-majlis/Wikipedia-API)
- better_profanity [Here](https://github.com/snguyenthanh/better_profanity)

> Example: `pip install scratchattach` (Command Prompt or Bash)

# Instructions for use

Once cloned, run the "main.py" script once and close the program using the included tkinter gui by clicking the button "Kill Program."
From there, create a .env file in the root of the directory. <br>Structure it like this:

- username="your username here"
- project_id="your project id here"
- session_id="your session id here"

Once finished, run "main.py" and load your scratch project.  
Everything should now be functional.
