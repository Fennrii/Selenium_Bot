from selenium import webdriver
from selenium.webdriver import ActionChains
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.wait import WebDriverWait
from bs4 import BeautifulSoup as BS
from time import sleep
import re
import os

if (not os.path.exists("./txtFiles")):
	os.mkdir("./txtFiles")
if (not os.path.exists("./csvFiles")):
	os.mkdir("./csvFiles")


# Creates a new text file using the url as the file name and copies all text from the main webpage ignoring headers and footers
def toFile(url, content):
	print("Creating text file")
	try:
		f = open("./txtFiles/" + url.replace("/", "\\") + ".txt", "x")
	except:
		f = open("./txtFiles/" + url.replace("/", "\\") + ".txt", "w")
	f.write(content.text)
	f.close()
# Creates a new CSV file using the url as the file name and copies the table (Currently only works for the first table on a webpage)
def toCsv(url, content):
	print("Creating CSV file")
	try:
		f = open("./csvFiles/" + url.replace("/", "\\") + ".csv", "x")
	except:
		f = open("./csvFiles/" + url.replace("/", "\\") + ".csv", "w")
	f.close()
	table = content.find_element(By.TAG_NAME, "table")
	print("table element found")
	elements = table.get_attribute("innerHTML")
	print("retrieved elements")
	soup = BS(elements, features="html.parser")
	print("Soup made")
	# Seperates all csv rows by getting the contents of each tr element
	rows = [tr.find_all('td') for tr in soup.find_all('tr')]
	print("rows created")
	print(len(rows))
	for i in rows:
		with open("./csvFiles/" + url.replace("/", "\\") + ".csv", "a") as f:
			f.write(", ".join(re.sub("<.*?>","",str(e)) for e in i) + "\n")

# Makes sure that the Chrome service is installed then sets it as the browser to be interfaced with REDO
sleep(10)

options = webdriver.ChromeOptions()
options.add_argument('--whitelisted-ips')
options.add_argument('--verbose')
options.add_argument('--disable-dev-shm-usage')

driver = webdriver.Remote('http://selenium:4444/wd/hub', 
							options=options)
startUrl= "https://www.nextgen.com/api"
sleep(5)
driver.get(startUrl)
ac = ActionChains(driver)
content = driver.find_element(By.TAG_NAME, "main")
# If there is a table on the webpage then copy it to a csv file
try:
	table = driver.find_element(By.TAG_NAME, "table")
	print("Table found")
	toCsv(driver.current_url, content)
except:
	print("No table found")
# Copies the webpage to a .txt file
toFile(driver.current_url, content)
print("Finished")
linkList = content.find_elements(By.TAG_NAME, 'a')
linkCount,  iterCount = 0,0
visitedLinks = []
visitedLinks.append("https://www.nextgen.com/api")
while iterCount < 8:
	link = linkList[linkCount]
	print("Navigating to: "+link.get_attribute("href"))
	# Skipps link if it has already been visited, is a file to download, or visits a community page that requires a login
	if (link.get_attribute("href").__contains__(".community")):
		print("Skipped link. Reason: Login required")
		linkCount += 1
		continue 
	elif(link.get_attribute("href").__contains__(".xslx")):
		print("Skipped link. Reason: Downloadable file")
		linkCount += 1
		continue 
	elif(visitedLinks.__contains__(link.get_attribute("href"))):
		print("Skipped link. Reason: Already visited")
		linkCount += 1
		continue 
	visitedLinks.append(link.get_attribute("href"))
	# Scrolls to the next unopened link (The scroll_to_element function was not working)
	clicked = False
	while not clicked:
		try:
			link.click()
			clicked = True
		except:
			ac.scroll_by_amount(0,50).perform()
	# Switches to the newly opened tab 
	if len(driver.window_handles) > 1:
		driver.switch_to.window(driver.window_handles[1])
	# Used to wait until the webpage is loaded so as to copy the proper webpage
	element = WebDriverWait(driver, 10).until(EC.url_changes(startUrl))
	content = driver.find_element(By.TAG_NAME, "main")
	# If there is a table on the webpage then copy it to a csv file
	try:
		table = driver.find_element(By.TAG_NAME, "table")
		print("Table found")
		toCsv(driver.current_url, content)
	except:
		print("No table found")
	# Copies the webpage to a .txt file		
	toFile(driver.current_url, content)
	print("Finished")
	# If the link opened in a new tab then closes new tab and switchs back to the start tab
	if len(driver.window_handles) > 1:
		driver.close()
		# Switches back to the origional tab to go to the next link
		driver.switch_to.window(driver.window_handles[0])
		print("Returned to start page")
	# If the link opened in the same tab then returns to the start with a simple back function
	else:
		driver.back()
		print("Returned to start page")
		# Used to wait until the webpage is loaded so as to not use the wrong webpage's links
		element = WebDriverWait(driver, 10).until(EC.url_matches(startUrl))
		# linkList needs to be refreshed to avoid stale links
		content = driver.find_element(By.TAG_NAME, "main")
		linkList = content.find_elements(By.TAG_NAME, 'a')
	linkCount += 1
	iterCount += 1
# Used to wait until the webpage is loaded so as to not quit prematurely
element = WebDriverWait(driver, 10).until(EC.url_matches(startUrl))
driver.quit()


