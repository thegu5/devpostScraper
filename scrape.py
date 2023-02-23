import requests
from bs4 import BeautifulSoup
import json
from time import gmtime, strftime
from tqdm import tqdm

# This is the hackathon's identifier that can be found in the url
print("Hackathon id (the devpost subdomain)")
hackathon_name = input("> ")

# DO NOT EDIT BELOW THIS LINE
hackathon_url = f"https://{hackathon_name}.devpost.com/project-gallery"

response = requests.get(hackathon_url, headers={"User-Agent": "Mozilla/5.0"})
soup = BeautifulSoup(response.text, "html.parser")

# Find the last page link
pagination = soup.find("ul", {"class": "pagination"})
last_page = 1
if pagination:
    last_page_link = pagination.find_all("a")[-2]
    last_page = int(last_page_link.text)


def parse_divs(webpage):
    projs = []
    divs = webpage.find_all("div", {"class": "software-entry gallery-entry fade visible"})
    for div in divs:
        proj = {}
        proj["name"] = div.find("h5").text.strip()
        proj["url"] = div.parent["href"]
        creators = div.find_all("img", class_="user-photo")
        proj["creators"] = [creator["title"] for creator in creators]
        projs.append(proj)
    return projs


# Scrape projects on each page
projects = []
users = []
for page in tqdm(range(1, last_page + 1), desc="Scraping project pages", unit="pages"):
    url = f"{hackathon_url}?page={page}"
    response = requests.get(url, headers={"User-Agent": "Mozilla/5.0"})
    soup = BeautifulSoup(response.text, "html.parser")
    project_divs = soup.find_all("a", {"class": "block-wrapper-link fade link-to-software"})
    for project_div in project_divs:
        projects.append(project_div["href"])
        user_cards = project_div.find_all("img", class_="user-photo")
        users += [user_card["title"] for user_card in user_cards]
# At this point, projects will be an array of urls and users will be an array of usernames

for user in tqdm(users, desc="Scraping user details", unit="users"):
    if user == "":
        continue
    url = f"https://devpost.com/{user}"
    response = requests.get(url, headers={"User-Agent": "Mozilla/5.0"})
    soup = BeautifulSoup(response.text, "html.parser")
    project_divs = soup.find_all("a", {"class": "block-wrapper-link fade link-to-software"})
    for project_div in project_divs:
        projects.append(project_div["href"])
    # replace the user's name with the user object
    # TODO: take into account user page pagination
print(projects)
# Scrape hackathons that each individual project submitted to
data = []
for project in tqdm(projects, desc="Scraping project details", unit="projects"):
    url = project
    response = requests.get(url, headers={"User-Agent": "Mozilla/5.0"})
    soup = BeautifulSoup(response.text, "html.parser")
    project = {}
    project["url"] = url
    submissions = soup.find("div", {"id": "submissions"})
    if submissions:
        hackathons = submissions.find_all("a")
        hackathon_names = [hackathon.text.strip() for hackathon in hackathons]
        project["hackathons"] = hackathon_names
    links = soup.find("ul", {"data-role": "software-urls"})
    project["links"] = []
    if links:
        links = links.find_all("a")
        project["links"] = [link["href"] for link in links]
    # THIS MIGHT BE BROKEN IDK
    project["video"] = ""
    video = soup.find("a", {"class": "ytp-title-link yt-uix-sessionlink"})
    if video:
        project["video"] = video["href"]
    container = soup.find("div", {"id": "app-details-left"})
    if container:
        container = container.find_all("div", {"class": None})
        project["description"] = container[-1].get_text()
    data.append(project)

# remove empty hackathon strings
for project in data:
    if "hackathons" in project:
        project["hackathons"] = [hackathon for hackathon in project["hackathons"] if hackathon]

timenow = strftime("%Y-%m-%d-%H:%M:%S", gmtime())
with open(f"{hackathon_name}-{timenow}.json", "w") as f:
    json.dump(data, f, indent=4)
