import csv
import time
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.common.exceptions import TimeoutException
from selenium.common.exceptions import StaleElementReferenceException
from selenium.common.exceptions import NoSuchElementException
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

# Function to get professor information
def get_professor_info(row, driver):
    sid, school_name, school_url, professors_url = row

    print(f"\nChecking professors at {school_name} using {professors_url}")
    driver.get(professors_url)
    
    professors_info_list = []
    max_show_more_clicks = 1  # Limit the number of "Show More" clicks to prevent infinite loop

     # Initialize teacher_cards as an empty list
    teacher_cards = []

    print("Loading professors...")

    # Check if the "Show More" button is available and click it to load more professors
    while max_show_more_clicks > 0:
        try:
            show_more_button = WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.XPATH, "//button[contains(text(), 'Show More')]")))

            # Attempt to close the overlay (if present) before clicking "Show More"
            try:
                overlay = driver.find_element(By.CSS_SELECTOR, '.ReactModal__Overlay')
                driver.execute_script("arguments[0].click();", overlay)
            except NoSuchElementException:
                pass

            # Scroll the "Show More" button into view before clicking it
            driver.execute_script("arguments[0].scrollIntoView();", show_more_button)
            driver.execute_script("arguments[0].click();", show_more_button)

            # Custom wait condition to wait for new professor cards to load
            WebDriverWait(driver, 10).until(
                lambda driver: len(driver.find_elements(By.CSS_SELECTOR, '.TeacherCard__StyledTeacherCard-syjs0d-0.dLJIlx')) > len(teacher_cards)
            )

            # Wait for some time to let the content stabilize
            time.sleep(0.5)

            # Re-find the "Show More" button after the click to avoid StaleElementReferenceException
            teacher_cards = driver.find_elements(By.CSS_SELECTOR, '.TeacherCard__StyledTeacherCard-syjs0d-0.dLJIlx')
            max_show_more_clicks -= 1

        except StaleElementReferenceException:
            print("StaleElementReferenceException occurred. Retrying...")
            continue
        except TimeoutException:
            print("No more professors to load.")
            break

    soup = BeautifulSoup(driver.page_source, 'html.parser')
    teacher_cards = soup.find_all('a', class_='TeacherCard__StyledTeacherCard-syjs0d-0 dLJIlx')

    if not teacher_cards:
        print(f"No professor information found for {school_name}")
    else:
        print("Finding reviews for", len(teacher_cards), f"teachers at {school_name}")
    for card in teacher_cards:
        name = card.find('div', class_='CardName__StyledCardName-sc-1gyrgim-0').text.strip()
        department = card.find('div', class_='CardSchool__Department-sc-19lmz2k-0').text.strip()
        overall_quality_elem = card.find('div', class_='CardNumRating__CardNumRatingNumber-sc-17t4b9u-2')
        overall_quality = overall_quality_elem.string.strip() if overall_quality_elem else "N/A"
        professor_url = 'https://www.ratemyprofessors.com' + card['href']

        print(f"Found teacher information for {name}")

        # Go to professor URL
        driver.get(professor_url)

        # Check if reviews are available for the professor
        if "No Ratings" in driver.page_source:
            print(f"No reviews found for {name}")
            continue

        review_soup = BeautifulSoup(driver.page_source, 'html.parser')
        review_section = review_soup.find('div', class_='Rating__StyledRating-sc-1rhvpxz-1')

        if not review_section:
            print(f"No reviews found for {name}")
            continue  # Skip to the next professor

        # Extract review information
        quality = review_section.find('div', string='Quality').find_next('div').string.strip()
        difficulty = review_section.find('div', string='Difficulty').find_next('div').string.strip()
        reviews = review_soup.find_all('div', class_='Rating__RatingInfo-sc-1rhvpxz-3')
        num_reviews = len(reviews)
        print(f"Found {num_reviews} reviews for {name}")

        for review in reviews:
            # Extract review details
            class_taken_elem = review.find('div', class_='RatingHeader__StyledClass-sc-1dlkqw1-3 eXfReS')
            try:
                class_taken = class_taken_elem.contents[-1]
            except AttributeError:
                class_taken = "N/A"

            review_date = review.find('div', class_='TimeStamp__StyledTimeStamp-sc-9q2r30-0').string.strip()
            review_text = review.find('div', class_='Comments__StyledComments-dzzyvm-0').string.strip()

            # Append the extracted data to professor_info_list
            professors_info_list.append([sid, school_name, name, overall_quality, num_reviews,
                                            department, class_taken, review_date, quality, difficulty, review_text])


    return professors_info_list


def extract_professors_info():
    options = Options()
    options.add_argument("--headless")  # Run Chrome in headless mode (without GUI)
    driver = webdriver.Chrome(options=options)

    with open('valid_urls.csv', 'r') as file:
        reader = csv.reader(file)
        next(reader)  # Skip the header row
        professors_info_list = []

        for row in reader:
            professor_info = get_professor_info(row, driver)
            if professor_info:
                professors_info_list.extend(professor_info)

    driver.quit()
    return professors_info_list


def save_to_csv(professors_info_list):
    with open('data/professors_info.csv', 'w', newline='') as file:
        writer = csv.writer(file)
        writer.writerow(['SID', 'School Name', 'Professor Name', 'Overall Quality', 'Num Reviews',
                         'Department', 'Class Taken', 'Review Date', 'Quality', 'Difficulty', 'Review Text'])
        writer.writerows(professors_info_list)


if __name__ == '__main__':
    professors_info_list = extract_professors_info()
    if professors_info_list:
        save_to_csv(professors_info_list)
        print("Data saved to 'professors_info.csv' successfully.")
    else:
        print("No professor information found.")

