## Arael

- tool for logging all your keystrokes into a local sqlite file
- initialize venv and install deps: `python3 -m venv arael && source arael/bin/activate && pip install -r requirements.txt`

### Arael CLI — Available Commands:

    help       : Show this help message.
    start      : Start the keylogger.
    status     : Check if Arael is running.
    stop       : Stop the keylogger.



### example usage:
    > python3 -m venv arael && source arael/bin/activate && pip install -r requirements.txt
    > python3 ctl.py start

### todo
- analytics ;) 
- typing speed monitoring
- maybe feed your keylogs into an llm?