import os
import re

from discord import Colour
from bs4 import BeautifulSoup
import requests
import discord
from datetime import datetime

MENU_URL = 'https://www.rit.edu/fa/diningservices/daily-specials'
HOURS_URL = 'https://www.rit.edu/fa/diningservices/places-to-eat/hours'


def get_menu(loc_arg):

    page = requests.get(MENU_URL)
    soup = BeautifulSoup(page.content, 'html.parser')
    #content = soup.find('div', class_='ds-output')

    loc_ids = {'bcc': "103", 'cmc': "104", 'tc': "105", 'gracies': "107"}

    meals = {'DINNER', 'LUNCH', 'BREAKFAST'}

    menu_tag = soup.find(id=loc_ids.get(loc_arg))
    loc_name = menu_tag.find('h3').text

    menus = menu_tag.find('div', class_='ds-loc-title')

    if not menus.contents:
        print(loc_name + ' is closed today.')
    else:
        print('Showing  menus for: ' + loc_name)
        for menu in menus.findChildren(recursive=False): #only find direct children, the menu <BREAKFAST-107>

            menu_name = menu.find('div', class_='menu-type').text

            items_section = menu.find('div', class_='col-xs-12 col-md-12 menu-category-items')

            if items_section is None:
                print('No ' + menu_name + ' today.')
            else:
                print(menu_name)

            stations = items_section.find_all('div', class_='col-xs-12 col-md-6 menu-category-list') # b/c there is another div class='clear'
            for item in stations:
                station_name = item.find('div', class_='menu-category').text
                dish = item.find('div', class_='menu-items')

                dish_string = ""
                for content in dish.contents[:-1]: # there is a new line at the end
                    if str(content) != '<br/>':
                        dish_string += '- ' + str(content) + '\n'

                print('Station: ' + station_name)
                print(dish_string)


def get_hours(is_include_closed):
    current_time = datetime.now()
    time_regex = re.compile(r'(1[012]|[1-9]):([0-5][0-9])(am|pm)')

    page = requests.get(HOURS_URL)
    soup = BeautifulSoup(page.content, 'html.parser')

    places = soup.find_all('div', class_='hours-title')

    for place in places:

        print(place.text.strip())

        time_frame = place.find_next_sibling('div')

        heading = time_frame.find('div', class_='row panel-heading')
        print(heading.text)

        # loops through the time containers until next hours-title and there is another sibling (for the last place specifically)
        while ' '.join(time_frame.attrs['class']) == 'container-fluid location-box panel panel-default hours-all-panel':

            time = time_frame.find('div', class_='row panel-body')

            time_groups = time_regex.findall(time.text)

            if not time_groups and is_include_closed: # regex would not match 'Closed', the array is empty

                print('(closed) all day')

            else:

                start_hour = int(time_groups[0][0])
                start_minute = int(time_groups[0][1])
                start_meridiem = time_groups[0][2]
                end_hour = int(time_groups[1][0])
                end_minute = int(time_groups[1][1])
                end_meridiem = time_groups[1][2]

                start_hour = (start_hour % 12) + 12 if start_meridiem == 'pm' else start_hour
                end_hour = (end_hour % 12) + 12 if end_meridiem == 'pm' else end_hour

                place_hours = time.find('div', class_='col-sm-5').text.strip()

                start_datetime = current_time.replace(hour=start_hour, minute=start_minute)
                end_datetime = current_time.replace(hour=end_hour, minute=end_minute)

                if start_datetime <= current_time <= end_datetime:
                    print('(open) Time is: ' + place_hours)
                elif is_include_closed:
                    print('(closed) Time was: ' + place_hours)

            next_time_frame = time_frame.find_next_sibling('div')

            if next_time_frame:
                time_frame = next_time_frame
            else:
                break

        print('\n')


#get_menu('gracies')
#get_menu('bcc')
get_hours(True)