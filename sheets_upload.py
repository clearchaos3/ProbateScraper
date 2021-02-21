from pydrive.auth import GoogleAuth
from pydrive.drive import GoogleDrive
import httplib2
import apiclient.discovery
from oauth2client.service_account import ServiceAccountCredentials

JSON_FILE = './client_secrets.json'
gauth = GoogleAuth()
scope = ['https://www.googleapis.com/auth/drive']
gauth.credentials = ServiceAccountCredentials.from_json_keyfile_name(JSON_FILE, scope)
drive = GoogleDrive(gauth)

file1 = drive.CreateFile()
file1.SetContentFile('filteredList.csv')
file1.Upload()

permission = file1.InsertPermission({
                        'type': 'anyone',
                        'value': 'anyone',
                        'role': 'reader'})

print(file1['alternateLink']) 

print('title: %s, id: %s' % (file1['title'], file1['id']))
