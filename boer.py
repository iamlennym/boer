from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException
import json
import argparse
from PIL import Image

class Session:
	def __init__(self):
		self.save_area = False

	def allDataProvided(self):
		if self.data['account']['login'] is None or self.data['account']['login'].strip() == "":
			print("The login is empty...")
			return False
		if self.data['account']['password'] is None or self.data['account']['password'].strip() == "":
			print("The password is empty...")
			return False

		return True

	def loadConfig(self, configFile):
		# open the file containing the JSON data
		try:
			with open(configFile, 'r') as f:
				# read the contents of the file into a string
				json_str = f.read()
		except FileNotFoundError:
			# handle the exception when the file is not found
			print("Error: Specified file(" + configFile + " not found.")
			return None

		# Parse the JSON document into a Python object
		self.data = json.loads(json_str)
		return self.data

	def login(self):
		# set up the Chrome driver
		self.driver = webdriver.Chrome()

		# navigate to the sign-in page
		self.driver.get("https://app.harness.io/auth/")
		self.driver.set_window_size(self.data['window']['width'], self.data['window']['height'])
		self.driver.find_element(By.ID, "email").send_keys(self.data['account']['login'])
		self.driver.find_element(By.ID, "password").send_keys(self.data['account']['password'])
		self.driver.find_element(By.ID, "email").click()
		self.driver.find_element(By.CSS_SELECTOR, ".primary").click()

		# wait for the dashboard page to load
		dashboard_title = "Dashboard | Harness"

		wait = WebDriverWait(self.driver, 20)
		try:
			wait.until(EC.title_is(dashboard_title))
		except TimeoutException:
			# handle the exception when the timeout occurs
			print("Error: Timed out waiting for page to load.")
			return None

		print("Succesfully logged in!!!")
		return self
	
	def makeScreenshot(self, url, x, y, w, h, fn):
		# Load the URL
		self.driver.get(url)

		wait = WebDriverWait(self.driver, 20)
		try:
			wait.until(EC.presence_of_element_located((By.ID, 'resact-root')))
		except TimeoutException:
			# handle the exception when the timeout occurs
			print("Error: Timed out waiting for page to load.")
			# return None

		try:
			self.driver.find_element(By.CSS_SELECTOR, ".bp3-icon-minus > svg").click()
		except Exception:
			print("Ignoring exception when trying to minimise the actions...")

		# take a screenshot of the page
		self.driver.save_screenshot(fn)

		# crop the image to the right dimensions
		# and save the cropped image to a file
		image = Image.open(fn)
		box = (x, y, w, h)
		cropped_image = image.crop(box)
		cropped_image.save(fn)

		return fn

	def makeAllScreenShots(self):
		# Iterate over the elements in the "fruits" array
		for screenshot in self.data['screenshots']:
			print(screenshot['url'], screenshot['left'], screenshot['top'], screenshot['width'], screenshot['height'], screenshot['outputfile'])
			self.makeScreenshot(screenshot['url'], screenshot['left'], screenshot['top'], screenshot['width'], screenshot['height'], screenshot['outputfile'])
		return self

	def quit(self):
		# close the browser
		self.driver.quit()
	
	#def print_info(self):
		#print("Name: {}, Age: {}".format(self.name, self.age))


# ---------------------------------------------------------------------------------------
#	Main script starts here.
# ---------------------------------------------------------------------------------------
parser = argparse.ArgumentParser()
parser.add_argument('--file', help='File containing the instruction set', required=True)
args = parser.parse_args()
print('Instruction File : {}'.format(args.file))

# Create a new instance of the Person class
session = Session()

session.loadConfig(args.file)

if session.allDataProvided() == True:
	if session.login() != None:
		session.makeAllScreenShots()
	
session.quit()
