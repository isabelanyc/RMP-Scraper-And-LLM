import csv
import requests
from bs4 import BeautifulSoup

def is_valid_url(url):
    response = requests.get(url)
    return response.status_code == 200

def get_school_name_and_professors_url(url):
    try:
        response = requests.get(url)
        if response.status_code == 200:
            soup = BeautifulSoup(response.content, 'html.parser')
            school_name_element = soup.find('div', class_='HeaderDescription__StyledTitleName-sc-1lt205f-1 eNxccF')
            professors_link_element = soup.find('a', class_='SchoolTitles__StyledProfLink-sc-3rec2n-2 kOZsZt')
            if school_name_element and professors_link_element:
                school_name = school_name_element.find('span').get_text(strip=True)
                professors_url = f"https://www.ratemyprofessors.com{professors_link_element['href']}"
                return school_name, professors_url
    except requests.exceptions.RequestException as e:
        print(f"Error retrieving school data for URL {url}: {e}")
    return None, None

def test_urls_and_save_to_csv():
    base_url = "https://www.ratemyprofessors.com"
    schools_tested = 0
    schools_found = 0
    schools_not_found = 0

    try:
        with open('urls.csv', mode='r', newline='', encoding='utf-8-sig') as infile, open('valid_urls.csv', mode='w', newline='') as outfile:
            reader = csv.reader(infile)
            writer = csv.writer(outfile)
            writer.writerow(['SID', 'School Name', 'School URL', 'School Professors URL'])

            next(reader)  # Skip the header row
            for row in reader:
                if len(row) >= 2:
                    sid = row[0].strip()
                    url = row[1].strip()
                    schools_tested += 1
                    print(f"Testing URL: {url}")

                    # Check if the URL is not empty and is valid
                    if url and is_valid_url(url):
                        school_name, professors_url = get_school_name_and_professors_url(url)
                        if school_name and professors_url:
                            schools_found += 1
                            writer.writerow([sid, school_name, url, professors_url])
                        else:
                            schools_not_found += 1
                            print(f"School name not found for SID: {sid}")
                    else:
                        schools_not_found += 1
                        print(f"Invalid URL for SID: {sid}")

                    # Print a message every 200 tests
                    if schools_tested % 200 == 0:
                        print("Still testing URLs...")

    except FileNotFoundError:
        print("Error: 'urls.csv' file not found.")
    except Exception as e:
        print(f"An error occurred: {e}")

    print("Number of schools tested:", schools_tested)
    print("Number of schools found:", schools_found)
    print("Number of schools not found:", schools_not_found)

if __name__ == "__main__":
    test_urls_and_save_to_csv()
