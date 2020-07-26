import pandas as pd
from geopy.geocoders import MapBox
import json
import time
from tqdm import tqdm


## Original dataframe has 661,218 row entries ##


NAICS_SECTOR_LIST = [
                    [ ' Agriculture, Forestry, Fishing and Hunting', '11'], 
                    [ ' Mining, Quarrying, and Oil and Gas Extraction', '21'],
                    [ ' Utilities', '22'],
                    [ ' Construction', '23'],
                    [ ' Manufacturing - Food and Textiles', '31'],
                    [ ' Manufacturing - Materials', '32'],
                    [ ' Manufacturing - Miscellaneous', '33'],
                    [ ' Wholesale Trade', '42'],
                    [ ' Retail Trade', '44'],
                    [ ' Retail Trade - General Merchandise', '45'],
                    [ ' Transportation and Warehousing - Support', '48'],
                    [ ' Transportation and Warehousing - General', '49'],
                    [ ' Information', '51'],
                    [ ' Finance and Insurance', '52'],
                    [ ' Real Estate and Rental and Leasing', '53'],
                    [ ' Professional, Scientific, and Technical Services', '54'],
                    [ ' Management of Companies and Enterprises', '55'],
                    [ ' Administrative and Support and Waste Management and Remediation Services', '56'],
                    [ ' Educational Services', '61'],
                    [ ' Health Care and Social Assistance', '62'],
                    [ ' Arts, Entertainment, and Recreation', '71'],
                    [ ' Accommodation and Food Services', '72'],
                    [ ' Other Services', '81'],
                    [ ' Religious Organizations', '8131'],
                    [ ' Labor Unions and Similar Labor Organizations', '81393'],
                    [ ' Political Organizations', '81394'],
                    [ ' Private Households', '814'],
                    [ ' Consumer Goods Repair', '811'],
                    [ ' Personal Services', '812'],
                    [ ' Government Support', '92'],
                    [ ' Unclassified Establishments', '99'],
                    [ ' Unreported Business Type', 'na']
                    ]   


geolocator = MapBox(api_key='pk.eyJ1IjoiZnV6enlsb2dpYzEzIiwiYSI6ImNrY2xjOGR5NTF4eWcycm5xYjY5eXA5ejUifQ.o3nz27PTtPI5JxztLiw_Tw')


def testAddress(address):
    location = geolocator.geocode(address)
    print(location.address)
    print((location.latitude, location.longitude))


def addressCleanup(df, stateName):
    df['Zip'] = df['Zip'].fillna(0.0).astype(int)
    #, expand= True)
    df['Address'] = df.Address.str.split(pat='BLDG').str[0]
    df['Address'] = df.Address.str.split(pat='Bldg').str[0]
    df['Address'] = df.Address.str.split(pat='bldg').str[0]
    
    df['Address'] = df.Address.str.split(pat='BUILDING').str[0]
    df['Address'] = df.Address.str.split(pat='Building').str[0]
    df['Address'] = df.Address.str.split(pat='building').str[0]
    df['Address'] = df['Address'].str.split(pat='STE').str[0]
    df['Address'] = df.Address.str.split(pat='Ste').str[0]
    df['Address'] = df['Address'].str.split(pat='ste').str[0]
    
    
    df['Address'] = df['Address'].str.split(pat='SUITE').str[0]
    df['Address'] = df.Address.str.split(pat='Suite').str[0]
    df['Address'] = df['Address'].str.split(pat='suite').str[0]
    df['Address'] = df['Address'].str.split(pat='#').str[0]
    df['Address'] = df['Address'].str.split(pat='PO BOX').str[0]
    df['Address'] = df['Address'].str.split(pat='P.O. BOX').str[0]
    df['Address'] = df['Address'].str.split(pat='PO Box').str[0]
    df['Address'] = df['Address'].str.split(pat='po box').str[0]
    df['Address'] = df['Address'].str.split(pat='p.o. box').str[0]

    df['Zip'] = df['Zip'].astype(str)

    for index, row in df.iterrows():
        if pd.isna(row['Address']):
            df.loc[int(index), 'lat-lon address'] = str(row['City']) + ', ' + stateName + ', 0' + str(row['Zip']) + ', ' + 'USA'
        else:
            df.loc[int(index), 'lat-lon address'] = str(row['Address']) + ', ' + str(row['City']) + ', ' + stateName + ', 0' + str(row['Zip']) + ', ' + 'USA'
 
    return df



def addColorColumn(df):
    '''
    Method creates a new column in the dataframe assigning 
    a color to each row based on the loan range found in 
    that row.  
    '''
    for index, row in df.iterrows():
        if str(row['LoanRange']) == 'a $5-10 million':
            df.loc[int(index), 'color'] = '#ff00ff'
        elif str(row['LoanRange']) == 'b $2-5 million':
            df.loc[int(index), 'color'] = '#00cc00' # #00ff00
        elif str(row['LoanRange']) == 'c $1-2 million':
            df.loc[int(index), 'color'] = '#FF0000'
        elif str(row['LoanRange']) == 'd $350,000-1 million':
            df.loc[int(index), 'color'] = '#0000ff'
        elif str(row['LoanRange']) == 'e $150,000-350,000':
            df.loc[int(index), 'color'] = '#fa8b02'

    return df


def addSectorSubsectorCols(df):
    '''
    Method will take the sector(first 2 digits) and subsector(first 3 digits)
    numbers out of the NAICS code and place them in new columns called
    Sector and Subsector.  the NAICS code column will be unchanged.
    If no NAICS code was provided, the new cols will show 'na' and 'nan'.
    '''
    for index, row in df.iterrows():
        if str(row['NAICSCode'])[:4] == '8131': # Religious Orgs
            df.loc[int(index), 'Sector'] = str(row['NAICSCode'])[:4]
            df.loc[int(index), 'Subsector'] = str(row['NAICSCode'])[:4]
            continue
        elif str(row['NAICSCode'])[:5] == '81393': # Labor Unions
            df.loc[int(index), 'Sector'] = str(row['NAICSCode'])[:5]
            df.loc[int(index), 'Subsector'] = str(row['NAICSCode'])[:5]
            continue
        elif str(row['NAICSCode'])[:5] == '81394': # Political Orgs
            df.loc[int(index), 'Sector'] = str(row['NAICSCode'])[:5]
            df.loc[int(index), 'Subsector'] = str(row['NAICSCode'])[:5]
            continue
        elif str(row['NAICSCode'])[:3] == '814': # Private Households
            df.loc[int(index), 'Sector'] = str(row['NAICSCode'])[:3]
            df.loc[int(index), 'Subsector'] = str(row['NAICSCode'])[:3]
            continue
        elif str(row['NAICSCode'])[:3] == '811': #Consumer Goods Repair
            df.loc[int(index), 'Sector'] = str(row['NAICSCode'])[:3]
            df.loc[int(index), 'Subsector'] = str(row['NAICSCode'])[:3]
            continue
        elif str(row['NAICSCode'])[:3] == '812': #Personal Services
            df.loc[int(index), 'Sector'] = str(row['NAICSCode'])[:3]
            df.loc[int(index), 'Subsector'] = str(row['NAICSCode'])[:3]
            continue

        df.loc[int(index), 'Sector'] = str(row['NAICSCode'])[:2]
        df.loc[int(index), 'Subsector'] = str(row['NAICSCode'])[:3]

    return df


def addressToLonLat(df, stateName):
    '''
    Method will convert address to lon/lat data and store new data 
    in new columns of the dataframe.  Any failed conversions will be 
    stored in a txt file in json format for further processing.
    Updated dataframe is returned. 
    '''
    fails_list = []
    for index, row in tqdm(df.iterrows(), total=df.shape[0], ncols=150):
        
        try:
            address_string = str(row['lat-lon address'])
            location = geolocator.geocode(address_string)
            # to test the calculated point lands in the USA
            us_check = verifyUsLatLong(location.latitude, location.longitude)
            if us_check is False: raise Exception()
            df.loc[int(index), 'Lat'] = location.latitude
            df.loc[int(index), 'Long'] = location.longitude
        except Exception as inst:
            print(' The following exception has been raised: ', inst )
            time.sleep(1)
            try:
                address_string = str(row['City']) + ' ' + stateName + ' ' + str(row['Zip'])
                location = geolocator.geocode(address_string)
                us_check = verifyUsLatLong(location.latitude, location.longitude)
                if us_check is False: raise Exception()
                df.loc[int(index), 'Lat'] = location.latitude
                df.loc[int(index), 'Long'] = location.longitude
            except Exception as inst:
                print(' A second exception has been raised: ', inst )
                address_string = str(row['City']) + ' ' + stateName
                try:
                    location = geolocator.geocode(address_string)
                    us_check = verifyUsLatLong(location.latitude, location.longitude)
                    if us_check is False: raise Exception()
                    df.loc[int(index), 'Lat'] = location.latitude
                    df.loc[int(index), 'Long'] = location.longitude
                except Exception:
                    fails_list.append(row['BusinessName'])
                continue

    with open('Master_Fail_List.txt', 'w') as f:
        json.dump(fails_list, f)

    return df


def zipToFiveDigit(df):
    df['Zip'] = df['Zip'].apply('{:0>5}'.format)


def cleanAndConvertStateAddress(stateName: str, stateAbbreviation: str, masterCSV: str) -> None:
    '''
    Mathod takes in the stateName as a string used to 
    name the csv file created.  masterCSV is used to 
    create a sub dataframe of the desired state
    '''
    # Convert the master CSV to a dataframe
    df = pd.read_csv(masterCSV)
    # Create a sub dataframe using desired state
    sub_df = df[df.State == stateAbbreviation]
    # Add color, sector, and subsector columns
    # sub_df = addColorColumn(sub_df)
    # sub_df = addSectorSubsectorCols(sub_df)
    # # Perform cleanup on address column
    sub_df = addressCleanup(sub_df, stateName)
    # Add leading zeros if zip is not 5 digits
    zipToFiveDigit(sub_df)
    # Convert the addresses to longitude and latitude
    sub_df = addressToLonLat(sub_df, stateName)
    # Save new dataframe to new state CSV file
    # sub_df.to_csv(r'new_' + stateName + '_ppp.csv', index=False)
    sub_df.to_csv(r'' + stateAbbreviation + '_new_test_file.csv', index=False)


def verifyUsLatLong(lat, lon):
    top = 49.3457868
    left = -124.7844079
    right = -66.9513812
    bottom = 24.7433195
    
    if not bottom <= lat <= top and left <= lon <= right:
        print(' out of U.S lat/lon')
        return False
    return True


 
if __name__ == '__main__':



    # state_name = 'VIRGIN ISLANDS'
    # state_abv = 'VI'
    # master_csv = '150k_plus_first_address_clean.csv'
    # # cleanAndConvertStateAddress(state_name, state_abv, master_csv)
    master_csv = 'test_file.csv'
    state_data = [
                ['MASSACHUSETTS', 'MA'],
                # ['PUERTO RICO', 'PR'], ['GUAM', 'GU'], ['NORTHERN MARIANA IS', 'MP'], ['VIRGIN ISLANDS', 'VI'],
                #['CONNECTICUT', 'CT'],  ['MASSACHUSETTS', 'MA'], ['NEW JERSEY', 'NJ'], ['AMERICAN SAMOA', 'AS']
                ]

    for i in state_data:
        state_name = i[0]
        state_abv = i[1]

        cleanAndConvertStateAddress(state_name, state_abv, master_csv)
    


    # ''' to check the number of rows per selected state '''
    # df = pd.read_csv('150k_plus_first_address_clean.csv')
    # sub = df[df['State'] == 'FL']
    # print(sub.shape[0])
    # address_dict = {'city': 'BLOOMFIELD', 'state': 'CT', 'zip': '06002', 'country': 'USA'}
    # address_string = '200 Post Road, , FAIRFIELD, CONNECTICUT, 06824, USA'
    # location = geolocator.geocode(address_string)
    # print(location)
    # print(location.latitude, location.longitude)

    # csv = 'test_file.csv'
    # df = pd.read_csv(csv)
    # zipToFiveDigit(df)
    # df = addressToLonLat(df)
    # df.to_csv(r'new_test_file.csv', index=False)

