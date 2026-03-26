# SI 201 HW4 (Library Checkout System)
# Your name: Devan Sarkar
# Your student id: 70234671
# Your email: dvsarkar@umich.edu
# Who or what you worked with on this homework (including generative AI like ChatGPT): ChatGPT
# If you worked with generative AI also add a statement for how you used it. 
# e.g.: I used ChatGPT to help me understand the code and how to approach each problem conceptually, and to better run my code first then debug it with ChatGPT
# Asked ChatGPT for hints on debugging and for suggestions on overall code structure
# Did your use of GenAI on this assignment align with your goals and guidelines in your Gen AI contract? If not, why?
# Yes they did, as I used GenAI to help me understand the code and how to approach each problem conceptually, and to better run my code first then debug it with ChatGPT. I did not use GenAI to write any of the code for me, but I did ask for suggestions on overall code structure and debugging help when I was stuck. I believe this aligns with my goals and guidelines in my Gen AI contract, as I used GenAI as a tool to enhance my understanding and problem-solving skills, rather than relying on it to do the work for me.
# --- ARGUMENTS & EXPECTED RETURN VALUES PROVIDED --- #
# --- SEE INSTRUCTIONS FOR FULL DETAILS ON METHOD IMPLEMENTATION --- #

from bs4 import BeautifulSoup
import re
import os
import csv
import unittest
import requests  # kept for extra credit parity


# IMPORTANT NOTE:
"""
If you are getting "encoding errors" while trying to open, read, or write from a file, add the following argument to any of your open() functions:
    encoding="utf-8-sig"
"""


def load_listing_results(html_path) -> list[tuple]:
    """
    Load file data from html_path and parse through it to find listing titles and listing ids.

    Args:
        html_path (str): The path to the HTML file containing the search results

    Returns:
        list[tuple]: A list of tuples containing (listing_title, listing_id)
    """
    # TODO: Implement checkout logic following the instructions
    # ==============================
    # YOUR CODE STARTS HERE
    # ==============================
    with open(html_path, "r", encoding="utf-8-sig") as f:
        soup = BeautifulSoup(f.read(), "html.parser")
    results = []
    title_divs = soup.find_all("div", attrs={"id": re.compile(r"^title_")}) #used AI here for formatting in the re.compile function, but I wrote the regex pattern myself to find divs with ids that start with "title_"
    for div in title_divs:
        listing_title = div.get_text(strip=True)
        listing_id = div["id"].replace("title_", "")
        results.append((listing_title, listing_id))
 
    return results
    pass
    # ==============================
    # YOUR CODE ENDS HERE
    # ==============================


def get_listing_details(listing_id) -> dict:
    """
    Parse through listing_<id>.html to extract listing details.

    Args:
        listing_id (str): The listing id of the Airbnb listing

    Returns:
        dict: Nested dictionary in the format:
        {
            "<listing_id>": {
                "policy_number": str,
                "host_type": str,
                "host_name": str,
                "room_type": str,
                "location_rating": float
            }
        }
    """
    # TODO: Implement checkout logic following the instructions
    # ==============================
    # YOUR CODE STARTS HERE
    # ==============================
    base_dir = os.path.abspath(os.path.dirname(__file__))
    filepath = os.path.join(base_dir, "html_files", f"listing_{listing_id}.html") #used os.path from AI for formatting 
    with open(filepath, "r", encoding="utf-8-sig") as f:
        soup = BeautifulSoup(f.read(), "html.parser")
    policy_number = ""
    policy_li_tags = soup.find_all("li", class_="f19phm7j")
    for li in policy_li_tags:
        li_text = li.get_text(strip=True)
        if "Policy number:" in li_text:
            value_span = li.find("span", class_="ll4r2nl") #used AI to help me with the li.find function
            if value_span:
                raw_policy = value_span.get_text(strip=True)
                raw_policy = raw_policy.replace("\ufeff", "").strip() #used AI for formatting here
                if raw_policy.lower() == "pending":
                    policy_number = "Pending"
                elif raw_policy.lower() == "exempt": 
                    policy_number = "Exempt"
                else:
                    policy_number = raw_policy
            break
    superhost_text = soup.find(string=re.compile(r"Superhost"))
    host_type = "Superhost" if superhost_text else "regular"
    host_name = ""
    hosted_by_tag = soup.find("h2", string=re.compile(r"Hosted by")) #used AI with re.compile to find the h2 tag that contains the host name, which starts with "Hosted by"
    if hosted_by_tag:
        hosted_text = hosted_by_tag.get_text(strip=True)
        host_name = hosted_text.replace("Hosted by ", "").strip()
    room_type = "Entire Room"
    subtitle_div = soup.find("div", class_="_cv5qq4")
    if subtitle_div:
        subtitle_text = subtitle_div.get_text(strip=True) #used AI to help me with the get_text function to extract the room type information from the subtitle div, which contains text like "Private Room in San Francisco" or "Shared Room in San Francisco"
        if "Private" in subtitle_text:
            room_type = "Private Room"
        elif "Shared" in subtitle_text:
            room_type = "Shared Room"
        else:
            room_type = "Entire Room"
    location_rating = 0.0
    location_elements = soup.find_all(string="Location")
    for elem in location_elements:
        parent = elem.parent
        grandparent = parent.parent
        texts = [t.strip() for t in grandparent.find_all(string=True) if t.strip()]
        if len(texts) == 2 and texts[0] == "Location":
            try:
                location_rating = float(texts[1])
            except ValueError:
                pass
    return {
        listing_id: {
            "policy_number": policy_number,
            "host_type": host_type,
            "host_name": host_name,
            "room_type": room_type,
            "location_rating": location_rating,
        }
    }
    # ==============================
    # YOUR CODE ENDS HERE
    # ==============================


def create_listing_database(html_path) -> list[tuple]:
    """
    Use prior functions to gather all necessary information and create a database of listings.

    Args:
        html_path (str): The path to the HTML file containing the search results

    Returns:
        list[tuple]: A list of tuples. Each tuple contains:
        (listing_title, listing_id, policy_number, host_type, host_name, room_type, location_rating)
    """
    # TODO: Implement checkout logic following the instructions
    # ==============================
    # YOUR CODE STARTS HERE
    # ==============================
    listings = load_listing_results(html_path)
    database = []
 
    for listing_title, listing_id in listings:
        details_dict = get_listing_details(listing_id) #used AI to help me with the function call to get_listing_details and to understand that it returns a nested dictionary, so I can extract the details for the current listing_id
        details = details_dict[listing_id]
        entry = (
            listing_title,
            listing_id,
            details["policy_number"],
            details["host_type"],
            details["host_name"],
            details["room_type"],
            details["location_rating"],
        )
        database.append(entry)
 
    return database
    pass
    # ==============================
    # YOUR CODE ENDS HERE
    # ==============================


def output_csv(data, filename) -> None:
    """
    Write data to a CSV file with the provided filename.

    Sort by Location Rating (descending).

    Args:
        data (list[tuple]): A list of tuples containing listing information
        filename (str): The name of the CSV file to be created and saved to

    Returns:
        None
    """
    # TODO: Implement checkout logic following the instructions
    # ==============================
    # YOUR CODE STARTS HERE
    # ==============================
    sorted_data = sorted(data, key=lambda x: x[6], reverse=True) #used Ai for the lambda function to sort the data by location rating, which is the 7th element in each tuple (index 6), in descending order
    with open(filename, "w", newline="", encoding="utf-8-sig") as f:
        writer = csv.writer(f)
        writer.writerow(
            [
                "Listing Title",
                "Listing ID",
                "Policy Number",
                "Host Type",
                "Host Name",
                "Room Type",
                "Location Rating",
            ]
        )
        for row in sorted_data:
            writer.writerow(row)
    pass
    # ==============================
    # YOUR CODE ENDS HERE
    # ==============================


def avg_location_rating_by_room_type(data) -> dict:
    """
    Calculate the average location_rating for each room_type.

    Excludes rows where location_rating == 0.0 (meaning the rating
    could not be found in the HTML).

    Args:
        data (list[tuple]): The list returned by create_listing_database()

    Returns:
        dict: {room_type: average_location_rating}
    """
    # TODO: Implement checkout logic following the instructions
    # ==============================
    # YOUR CODE STARTS HERE
    # ==============================
    room_type_ratings = {}
    for entry in data:
        room_type = entry[5]
        location_rating = entry[6]
        if location_rating == 0.0:
            continue
        if room_type not in room_type_ratings:
            room_type_ratings[room_type] = []
        room_type_ratings[room_type].append(location_rating)
    averages = {}
    for room_type, ratings in room_type_ratings.items():
        averages[room_type] = round(sum(ratings) / len(ratings), 1)
    return averages
    pass
    # ==============================
    # YOUR CODE ENDS HERE
    # ==============================


def validate_policy_numbers(data) -> list[str]:
    """
    Validate policy_number format for each listing in data.
    Ignore "Pending" and "Exempt" listings.

    Args:
        data (list[tuple]): A list of tuples returned by create_listing_database()

    Returns:
        list[str]: A list of listing_id values whose policy numbers do NOT match the valid format
    """
    # TODO: Implement checkout logic following the instructions
    # ==============================
    # YOUR CODE STARTS HERE
    # ==============================
    invalid_ids = []
    pattern1 = r"^20\d{2}-00\d{4}STR$"
    pattern2 = r"^STR-000\d{4}$" 
    for entry in data:
        listing_id = entry[1]
        policy_number = entry[2]
        if policy_number == "Pending" or policy_number == "Exempt":
            continue
        if not re.match(pattern1, policy_number) and not re.match(
            pattern2, policy_number
        ):
            invalid_ids.append(listing_id)
    return invalid_ids
    pass
    # ==============================
    # YOUR CODE ENDS HERE
    # ==============================


# EXTRA CREDIT
def google_scholar_searcher(query):
    """
    EXTRA CREDIT

    Args:
        query (str): The search query to be used on Google Scholar
    Returns:
        List of titles on the first page (list)
    """
    # TODO: Implement checkout logic following the instructions
    # ==============================
    # YOUR CODE STARTS HERE
    # ==============================
    url = "https://scholar.google.com/scholar"
    params = {"q": query}
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
    }
    response = requests.get(url, params=params, headers=headers)
    soup = BeautifulSoup(response.text, "html.parser")
    titles = []
    for h3 in soup.find_all("h3", class_="gs_rt"):
        title_text = h3.get_text(strip=True)
        titles.append(title_text)
    return titles
    pass
    # ==============================
    # YOUR CODE ENDS HERE
    # ==============================


class TestCases(unittest.TestCase):
    def setUp(self):
        self.base_dir = os.path.abspath(os.path.dirname(__file__))
        self.search_results_path = os.path.join(self.base_dir, "html_files", "search_results.html")

        self.listings = load_listing_results(self.search_results_path)
        self.detailed_data = create_listing_database(self.search_results_path)

    def test_load_listing_results(self):
        self.assertEqual(len(self.listings), 18)
        self.assertEqual(self.listings[0], ("Loft in Mission District", "1944564"))
        pass

    def test_get_listing_details(self):
        html_list = ["467507", "1550913", "1944564", "4614763", "6092596"]
        listing_details = [get_listing_details(lid) for lid in html_list]
        self.assertEqual(listing_details[0]["467507"]["policy_number"], "STR-0005349")
        self.assertEqual(listing_details[2]["1944564"]["host_type"], "Superhost")
        self.assertEqual(listing_details[2]["1944564"]["room_type"], "Entire Room")
        self.assertEqual(listing_details[2]["1944564"]["location_rating"], 4.9)
        pass

    def test_create_listing_database(self):
        for item in self.detailed_data:
            self.assertEqual(len(item), 7)
        self.assertEqual(self.detailed_data[-1], ("Guest suite in Mission District", "467507", "STR-0005349", "Superhost", "Jennifer", "Entire Room", 4.8))
        pass

    def test_output_csv(self):
        out_path = os.path.join(self.base_dir, "test.csv")
        out_path = os.path.join(self.base_dir, "test.csv")
        output_csv(self.detailed_data, out_path)
        with open(out_path, "r", encoding="utf-8-sig") as f:
            reader = csv.reader(f)
            rows = list(reader)
        self.assertEqual(rows[1], ["Guesthouse in San Francisco", "49591060", "STR-0000253", "Superhost", "Ingrid", "Entire Room", "5.0"])

        os.remove(out_path)

    def test_avg_location_rating_by_room_type(self):
        avg_ratings = avg_location_rating_by_room_type(self.detailed_data)
        self.assertEqual(avg_ratings["Private Room"], 4.9)

    def test_validate_policy_numbers(self):
        invalid_listings = validate_policy_numbers(self.detailed_data)
        self.assertEqual(invalid_listings, ["16204265"])

def main():
    detailed_data = create_listing_database(os.path.join("html_files", "search_results.html"))
    output_csv(detailed_data, "airbnb_dataset.csv")


if __name__ == "__main__":
    main()
    unittest.main(verbosity=2)