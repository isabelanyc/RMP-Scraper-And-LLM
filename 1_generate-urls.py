import csv
import random


def generate_urls_and_save_to_csv():
    base_url = 'https://www.ratemyprofessors.com/school/'

    
    # Generate URLs and store them in a list
    urls_data = []

    for i in range(1, 300):
        # generate random sid 
        sid = random.randint(1, 9999)
        url = f"{base_url}{sid}"
        urls_data.append((sid, url))

    # Save the URLs to a CSV file
    with open('data/urls.csv', mode='w', newline='') as file:
        writer = csv.writer(file)
        writer.writerow(['SID', 'URL'])
        writer.writerows(urls_data)

if __name__ == '__main__':
    generate_urls_and_save_to_csv()
    print("URLs generated and saved to 'urls.csv' successfully.")
