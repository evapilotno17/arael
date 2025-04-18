# Arael

- a tool for logging all your keystrokes into a local sqlite db

## How to run
- initialize the venv: `python3 -m venv arael` or `python -m venv arael`
- activate your venv: `source arael/bin/activate` (bash/zsh) `.\arael\Scripts\Activate.ps1` (powershell)
- install deps: `pip install -r requirementx.txt` (if you get errors installing a specific module on windows, remove that module from requirements.txt and re-run this command)

### Arael CLI — Available Commands:

    help                    : Show this help message.
    live                    : monitor your typing speed live!!
    regenerate_logs         : regenerate session logs into ./logs/ in a human readable way
    start      (--verbose)  : Awken arael. --verbose : stream arael stdout/stderr
    status                  : Check if Arael is running.
    stop                    : Stop the keylogger.

NOTE: to view your logs, you must run `python3 ctl.py regenerate_logs`. this will generate your logs folder underneath the same directory :)


### example usage:
    > python3 -m venv arael && source arael/bin/activate && pip install -r requirements.txt
    > python3 ctl.py start

## live typing speed graph

- run the command `python3 ctl.py live` to create a window which graphically shows your typing speed in real time!

- note that this command internally starts arael if it isn't already running

### analysing your keystroke data
- open up a jupyter session within your venv with the command `python3 -m jupyter lab`
- NOTE: don't run `jupyter lab` instead, as we want our jups to use the same kernel as the venv
- open the notebook `analytics.ipynb`
- enjoy analysing your keystroke data

### todo
- analytics on top of the collected data