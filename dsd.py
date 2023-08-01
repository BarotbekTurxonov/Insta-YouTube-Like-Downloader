from telethon.sync import TelegramClient, functions

api_id = 24720214
api_hash = "09ed497cc8083edb349dc55f1fa82b90"




with TelegramClient('session_name', api_id, api_hash) as client:
    result = client(functions.contacts.GetContactsRequest(
        hash=-12398745604826
    ))
    ids= []
    for i in result.to_dict()['contacts']:
        ids.append(i['user_id'])
        print(i)
    client(functions.contacts.DeleteContactsRequest(
            id=ids
        ))


