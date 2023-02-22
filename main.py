import argparse
import re
import folium
from haversine import haversine
from geopy.geocoders import Nominatim


def find_location(path: str) -> list:
    """
    The function find location from file
    :param path: path to file
    :return: name of location
    >>> find_location('film_loc')[:40]

    """
    # with open(path, 'r') as file:
    #     data = file.read()
    # return re.findall(r'[A-Z][a-z]+(?:\s[A-Z][a-z]+)*(?:,\s[A-Za-z]+){2}', data)
    # ----------------------
    list_of_location = []
    with open(path, 'r', encoding='latin-1') as f:
        for line in f:
            if line.startswith('"'):
                parts = line.split('\t')
                title_and_year = re.sub(r'\{.*?\}', '', parts[0].replace('#', '').replace('"', ''))
                location = parts[-1].strip()
                title = title_and_year.split('(')[0].strip()
                year = title_and_year.split('(')[-1].strip(')').strip()
                location_data = [title, year.replace(')', ''), location]
                list_of_location.append(location_data)
    return list_of_location


def take_coordinate(list_of_information: list) -> list:
    """
    The function find coordinate by location
    :param list_of_information: list with all needed information
    :return: coordinate
    # >>> (take_coordinate(find_location('locations.list')[:100]))
    # >>> take_coordinate(find_location('film_loc')[:100])
    """
    result = []
    for i in list_of_information:
        geolocator = Nominatim(user_agent="my_app_name", timeout=100)
        try:
            location = geolocator.geocode(i[2], timeout=100)
            result += [[i[0]] + [i[1]] + [location.latitude] + [location.longitude]]
        except AttributeError:
            continue
    return result


def filter_by_year(list_of_information: list, year: int) -> list:
    """
    The function filter list by year
    :param list_of_information: list
    :param year: year
    :return: filtered list
    # >>> filter_by_year(take_coordinate(find_location('locations.list')[:100]), 2014)
    # >>> filter_by_year(take_coordinate(find_location('film_loc')[:100]), 2014)
    """
    return list(filter(lambda x: int(x[1]) == year, list_of_information))


def create_map(year, lat, lon, path):
    """
    The function create map
    :param year:
    :param lat:
    :param lon:
    :param path:
    :return:
    """
    list_of_filtered_location = filter_by_year(take_coordinate(find_location(path)[:100]), year)
    m = folium.Map(location=[lat, lon], zoom_start=5)
    counter = 0
    for i in list_of_filtered_location:
        try:
            folium.Marker(location=[i[2], i[3]],
                          popup=f'Name of film: {i[0]}\nYear: {i[1]}\n Distance:'
                                f' {round(haversine((lat, lon), (i[2], i[3])), 2)}km',
                          icon=folium.Icon(color='maroon')).add_to(m)
            counter += 1
        except IndexError:
            continue
        if counter > 10:
            break
    folium.WmsTileLayer(
        url='http://mesonet.agron.iastate.edu/cgi-bin/wms/nexrad/n0r.cgi',
        name='test',
        fmt='image/png',
        layers='nexrad-n0r-900913',
        transparent=True,
    ).add_to(m)
    m.save('map.html')


def main():
    """

    :return:
    """
    parser = argparse.ArgumentParser(description='parser')

    parser.add_argument('year', type=str, help='The year')
    parser.add_argument('latitude', type=float, help='The lt')
    parser.add_argument('longitude', type=float, help='The ln')
    parser.add_argument('data', type=str, help='The path')
    args = parser.parse_args()
    # first = filter_by_year(take_coordinate(find_location(args.data)), args.year)
    create_map(args.year, args.latitude, args.longitude, args.data)


main()


