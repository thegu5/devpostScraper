import requests
from bs4 import BeautifulSoup
import json
from time import gmtime, strftime
from tqdm import tqdm

# This is the hackathon's identifier that can be found in the url
hackathon_name = "bay-area-hacks-society"

# DO NOT EDIT BELOW THIS LINE
hackathon_url = f"https://{hackathon_name}.devpost.com/project-gallery"

response = requests.get(hackathon_url, headers={"User-Agent": "Mozilla/5.0"})
soup = BeautifulSoup(response.text, "html.parser")

# Find the last page link
pagination = soup.find("ul", {"class": "pagination"})
last_page_link = pagination.find_all("a")[-2]
last_page = int(last_page_link.text)

# Scrape projects on each page
projects = []
for page in tqdm(range(1, last_page + 1), desc="Scraping project pages", unit="pages"):
    url = f"{hackathon_url}?page={page}"
    response = requests.get(url, headers={"User-Agent": "Mozilla/5.0"})
    soup = BeautifulSoup(response.text, "html.parser")
    project_divs = soup.find_all("div", {"class": "software-entry gallery-entry fade visible"})
    for project_div in project_divs:
        project_name = project_div.find("h5").text.strip()
        creators = project_div.find_all("img", class_="user-photo")
        creators_names = [creator["title"] for creator in creators]
        project_url = project_div.parent["href"]
        projects.append({"name": project_name, "creators": creators_names, "url": project_url})

# Scrape hackathons that each individual project submitted to
for project in tqdm(projects, desc="Scraping project details", unit="projects"):
    url = project["url"]
    response = requests.get(url, headers={"User-Agent": "Mozilla/5.0"})
    soup = BeautifulSoup(response.text, "html.parser")
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
    project["video"] = ""
    video = soup.find("a", {"class": "ytp-title-link yt-uix-sessionlink"})
    if video:
        project["video"] = video["href"]
    container = soup.find("div", {"id": "app-details-left"})
    if container:
        container = container.find_all("div", {"class": None})
        project["description"] = container[-1].get_text()

for project in projects:
    if "hackathons" in project:
        project["hackathons"] = list(filter(None, project["hackathons"]))

timenow = strftime("%Y-%m-%d-%H:%M:%S", gmtime())
with open(f"{hackathon_name}-{timenow}.json", "w") as f:
    json.dump(projects, f, indent=4)
