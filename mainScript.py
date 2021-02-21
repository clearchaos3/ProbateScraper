import requests
import pandas as pd
import re
# import
from bs4 import BeautifulSoup as bs

import time

output = []

startDate = input(
    'Enter start date of 7-day search in the format mm/dd/yyyy: ')
# startDate = '04/16/2020'

courts = [
    {
        'courtId': 'CT11',
        'courtDesc': '11th Judicial Circuit (St. Charles County)'
    },
    {
        'courtId': 'CT21',
        'courtDesc': '21st Judicial Circuit (St. Louis County)'
    },
]

search_url = 'https://www.courts.mo.gov/casenet/cases/filingDateSearch.do'
parties_url = 'https://www.courts.mo.gov/casenet/cases/parties.do'

# proxies = {'http': 'p.webshare.io:20000', 'https': 'p.webshare.io:20000'}

search_payload = {
    'inputVO.type': 'CT',
    'inputVO.courtId': '',
    'inputVO.errFlag': 'N',
    'inputVO.selectionAction': 'search',
    'inputVO.countyCode': '',
    'inputVO.juvenileUserFlag': 'N',
    'inputVO.countyDesc': 'All',
    'inputVO.selectedIndexCaseStatus': '0',
    'inputVO.courtDesc': '',
    'inputVO.locationDesc': '',
    'inputVO.selectedCaseType': 'All',
    'inputVO.selectedIndexCourt': '0',
    'courtId': '',
    'inputVO.startDate': startDate,
    'inputVO.caseStatus': 'A',
    'inputVO.caseType': 'Probate',
    'CountyId': '',
    'inputVO.locationCode': '',
    'findButton': 'Find',
}

next_page_payload = {
    'inputVO.caseType': 'Probate',
    'inputVO.startDate': startDate,
    'inputVO.errFlag': 'N',
    'inputVO.caseTypeDesc': '',
    'inputVO.selectionAction': 'search',
    'inputVO.courtId': '',
    'inputVO.courtDesc': '',
    'inputVO.countyDesc': 'All',
    'inputVO.countyCode': '',
    'inputVO.locationDesc': 'All',
    'inputVO.locationCode': '',
    'inputVO.caseStatus': 'A',
    'inputVO.type': 'CT',
    'inputVO.startingRecord': '',
    'inputVO.totalRecords': '',
    'inputVO.subAction': 'search',
}

header = [
    'FirstName', 'LastName', 'Relation', 'Street', 'Street2', 'City', 'State',
    'Zip', 'Business', 'YearOfBirth', 'DateOfDeath', 'RepName', 'RepTitle',
    'RepStreet', 'RepStreet2', 'RepCity', 'RepState', 'RepZip', 'RepPhone',
    'DateFiled', 'Name', 'CaseNo', 'StyleOfCase', 'CaseType', 'Location',
    'CreationDateTime'
]


def get_parties(person_template_dict, data):

    while True:

        res = requests.post(parties_url, data=data)

        if res.status_code == 200:

            break

        else:

            time.sleep(30)

    page = bs(res.content, 'lxml')

    tables = page.select('table.detailRecordTable')

    for table in tables:

        trs = table.select('tr')[0::2]

        for tr in trs:

            person_details = {}

            person_details.update(person_template_dict)

            for td_idx in range(1, 4, 2):

                f_name, l_name, relation = '', '', ''

                tds = tr.find_all('td')

                line1 = tds[td_idx].text.strip()

                line1 = ' '.join(line1.split())

                if len(line1.split(' , ')) == 3:

                    f_name, l_name, relation = line1.split(' , ')

                else:

                    break

                if 'guardian' in relation.lower() or 'minor' in relation.lower(
                ):

                    if output:

                        output.pop()

                    # continue

                    break

                tds = tr.find_next('tr').find_all('td')

                line2 = tds[td_idx].text.strip()

                values = line2.replace('\r', '').replace('\t', '').split('\n')

                values = [value.strip() for value in values if value.strip()]

                address1, address2, city, state, zip_code = '', '', '', '', ''

                for idx, value in enumerate(values):

                    # value == 'MO':
                    if re.search(r'[A-Z]{2}', value) and len(
                            value.strip()) == 2:

                        state = value

                        city = values[idx - 1]

                        zip_code = values[idx + 1]

                        if idx > 2:

                            address1 = values[0]

                            address2 = values[1]

                        else:

                            address1 = values[0]

                        break

                if td_idx == 1:

                    YoB = ''

                    for idx, value in enumerate(values):

                        if 'Year of Birth' in value:

                            YoB = values[idx + 1]

                            break

                    DoD = ''

                    for idx, value in enumerate(values):

                        if 'Date of Death' in value:

                            DoD = values[idx + 1]

                            break

                    person_details['FirstName'] = f_name

                    person_details['LastName'] = l_name

                    person_details['Relation'] = relation

                    person_details['Street'] = address1

                    person_details['Street2'] = address2

                    person_details['City'] = city

                    person_details['State'] = state

                    person_details['Zip'] = zip_code

                    person_details['YearOfBirth'] = YoB

                    person_details['DateOfDeath'] = DoD

                if td_idx == 3:

                    phone = ''

                    for idx, value in enumerate(values):

                        if 'Business:' in value:

                            phone = ' '.join(values[idx + 1:])

                            break

                    person_details['RepName'] = ' '.join([f_name, l_name])

                    person_details['RepTitle'] = relation

                    person_details['RepStreet'] = address1

                    person_details['RepStreet2'] = address2

                    person_details['RepCity'] = city

                    person_details['RepState'] = state

                    person_details['RepZip'] = zip_code

                    person_details['RepPhone'] = phone

                output.append(person_details)


def get_records(url, data):

    global header

    res = requests.post(url, data=data)

    page = bs(res.content, 'lxml')

    trs = page.select('tr[align=left]')[1:]

    for tr in trs:

        person_template_dict = {key: '' for key in header}

        tds = tr.select('td')[1:]

        person_template_dict['DateFiled'] = tds[0].text.strip()

        person_template_dict['CaseNo'] = tds[1].text.strip()

        person_template_dict['StyleOfCase'] = tds[2].text.strip()

        person_template_dict['CaseType'] = tds[3].text.strip()

        person_template_dict['Location'] = tds[4].text.strip()

        parties_payload = {
            'inputVO.caseNumber': person_template_dict['CaseNo'],
            'inputVO.courtId': data['inputVO.courtId'],
        }

        get_parties(person_template_dict, parties_payload)

    return page


for court in courts:

    print(f'Getting data for {court["courtDesc"]}')

    search_payload['inputVO.courtId'] = court['courtId']

    search_payload['courtId'] = court['courtId']

    search_payload['inputVO.courtDesc'] = court['courtDesc']

    next_page_payload['inputVO.courtId'] = court['courtId']

    next_page_payload['inputVO.courtDesc'] = court['courtDesc']

    page = get_records(search_url, search_payload)

    if page.select('.resultDescription'):

        display_text = page.select('.resultDescription')[0].text.strip()

    else:

        print(f'No results found for the court: {court["courtDesc"]}')

        continue

    if re.search(r'thru [\d]* of ([\d])*', display_text):

        totalRecords = eval(
            re.search(r'thru [\d]* of ([\d]*)', display_text).group(1))

    next_page_payload['inputVO.totalRecords'] = totalRecords

    startingRecord = 16

    if totalRecords > 15:

        while True:

            next_page_payload['inputVO.startingRecord'] = startingRecord

            get_records(search_url, next_page_payload)

            startingRecord += 15

            if startingRecord > totalRecords:

                break

df = pd.DataFrame(output, columns=header).drop_duplicates()
df[pd.isnull(df)] = None

#df.to_excel('output.xlsx', index=False)

df.to_csv('probatesScraped.csv', index=False)
