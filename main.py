import requests as req
import os, sys
sys.path.append(os.path.join(os.path.dirname(os.path.abspath(__file__)), '..'))
from db import get_db, insert, exists, create_connection
import json
from typing import List, Dict
import constants


TOKEN = "5012363836:AAHBsRGNPp1voCRwij7Q4UijsonT6OlFhwA"


 ### DO THE E?VENT LOOP THAT QUERIES FOR UPDATES EVERY SECOND
 ### READ THE UPDATES AND SEE WHAT IS GOING ON
 ### monitor chats and see if anyone has asked for the puzzle



class Requester:

    def __init__(self, http_method='GET'):
        self.http_method = http_method.lower()

    def __call__(self, params=None):

        return getattr(req, self.http_method)(self.url, params = params)


class TelegramRequester(Requester):

    def __init__(self, api_method='getUpdates', http_method='GET'):
        super().__init__(http_method=http_method)
        self.api_method = api_method
        self.url = f"https://api.telegram.org/bot{TOKEN}/{self.api_method}"


class ChessRequester (Requester):

    def __init__(self, http_method='GET'):
        super().__init__(http_method=http_method)
        self.url = "https://api.chess.com/pub/puzzle"


class Updates:

    def __init__(self, limit=100, allowed_updates=None):
        self.limit=limit
        self.allowed_updates=allowed_updates

    def get(self):
        r = TelegramRequester(api_method='getUpdates')
        params = {}
        if self.allowed_updates:
            params['allowed_updates'] = self.allowed_updates
        if self.limit:
            params['limit'] = self.limit
        self.updates=r(params=params)
        return self.updates

def get_chess_puzzle():

    c = ChessRequester()
    url = c().json()['image']
    sender = TelegramRequester('sendPhoto')
    params = {'photo':url, 'chat_id': get_chat('test')}
    sender(params=params)



def get_bot_chats():
    """Get all the chats the bot is in."""
    chat_ids_getter = Requester('getUpdates')
    updates = chat_ids_getter(params={'allowed_updates': 'my_chat_member'})
    response = updates.json()
    print(response)
    chats = []
    print([r for r in response['result'] if 'my_chat_member' in r.keys()])
    for r in response['result']:
        if 'my_chat_member' in r.keys():
            chats.append((int(r['my_chat_member']['chat']['id']), r['my_chat_member']['chat']['title']))

    for chat in chats:
        # inserting each chat into the table
        id_ = chat[0]
        title = chat[1]
        is_group = 0
        if id_ < 0:
            id_ = id_*-1
            is_group = 1

        if not exists('chats', 'chat_id', id_):
            insert('chats', {'chat_id': id_, 'title': title, 'is_group': is_group})



def test_bot():
    requester = Requester('getMe')
    response = requester()


def get_chat(title):

    stmt = f"select chat_id, is_group from chats where title = '{title}'"
    connection = create_connection()
    cursor = connection.cursor()
    cursor.execute(stmt)
    chat_id, is_group =  cursor.fetchone()
    if is_group:
        chat_id *= -1
    return chat_id



def write_message(chat_id):
    if chat_id == -240466722:
        return None
    requester = Requester('sendMessage')
    response = requester(params={'chat_id': chat_id, 'text': 'Hello, testing bot'})

    return response



class InvalidCommandError(Exception):
    def __init__(self, message):            
        # Call the base class constructor with the parameters it needs
        super().__init__(message)




class Commands:

    def __init__(self):
        self.commands = self._get()


    def _get(self):
        getter = TelegramRequester('getMyCommands')
        return getter().json()['result']

    def set(self, command_list: List[Dict]):
        params = {'commands': [dict(command=item['command'], description=item['description']) for item in command_list + self.commands]}
        r = req.get(f"https://api.telegram.org/bot{TOKEN}/setMyCommands?commands="+ str(json.dumps(params['commands'])))
        results = r.json()
        if results['ok']:
            self.commands = self._get()
            return r.json()
        elif results['description'] == 'Bad Request: BOT_COMMAND_INVALID':
            raise InvalidCommandError('Try removing spaces, uppercase, or punctuation from the command.') 
        else:
            return None


    def delete(self, command):
        # if command is only a string, make into a list
        if type(command) != list:
            command = [command]
        deleter = TelegramRequester('deleteMyCommands')
        response = deleter() 
        print('deleted', self.commands)
        if response.json()['ok']:
            self.commands = [com for com in self.commands if com['command'] not in command]
            self.set(self.commands)
            self.commands = response.json()['result']
            return response.json()
        else:
            return None

    def truncate(self):
        deleter = TelegramRequester('deleteMyCommands')
        r = deleter()
        self.commands = self._get()
        return r.json()




def establish_commands():
    """Initialise the commands for the Bot. """

    c = Commands()

    # delete lists of commands
    c.truncate()

    # set the commands
    c.set(constants.COMMANDS)







def main():


    establish_commands()


if __name__ == '__main__':
    
    main()