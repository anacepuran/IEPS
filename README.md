# IEPS project

The following project is the implementation of the multi threaded web crawler developed in Python.

Additional libraries included: bs4, psycopg2, hyperlink

POSTGRESQL SETUP:

1. Install postgresql (in the process you will be prompted to choose the password - I recommend "postgres")
2. Open SQL shell
3. Login with default values (port, host, name, ...) and enter the password chosen in the installation process (postgres)
4. Run the following commands:
   CREATE DATABASE spider; ... which creates the db
   \c spider ... which connects to the db
   \i 'path to the crawldb.sql file downloaded from moodle' ... which runs the script and initiates the db values
5. Now your local db should be set. Open the pgAdmin 4 web app (which was also installed with the shell and postgresql) and check whether the database was initiated correctly. Under schemas there should be one named crawldb!

''' # URl to web scrap from.
my_url = 'http://' + seed # opens the connection and downloads html page from url
uClient = uReq(my_url) # parses html into a soup data structure to traverse html
page_html = uClient.read()
uClient.close()
soup = BeautifulSoup(page_html, "html.parser")
links = soup.find_all('a', href=True)
for link in links:
url = link['href']
if (url.startswith('/') or url.startswith(seed)) and len(url) > 3:
frontier.append(urljoin(my_url, url))
if url.endswith(domains):
frontier.append(url)
print(frontier)
'''
