from pathlib import Path
from selenium import webdriver
from selenium.common.exceptions import InvalidSwitchToTargetException, TimeoutException, WebDriverException
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options

class PageItem(object):
	def __init__(self, label='', selector='', wait_for='', of_interest=False,
		index=[0,1], is_link=False, inferred_selector=None, range_name=None
	):
		self.label = label
		self.selector = selector
		self.start = index[0]
		self.end = index[1]
		self.wait_for = wait_for
		self.value = ''
		self.of_interest = of_interest
		self.range_name = range_name
		self.is_link = is_link
		self.inferred_selector = inferred_selector

class Website(object):
	def __init__(self, name, url, username='', password='', username_selector='',
		password_selector='', login_button_selector='', not_logged_in_title='', input_selector='',
		login_required=False, wait_for='', items_of_interest=[], homepage=None,
		captcha_selector=None
	):
		self.name = name
		self.url = url
		self.username = username
		self.password = password
		self.username_selector = username_selector
		self.password_selector = password_selector
		self.login_button_selector = login_button_selector
		self.login_title = not_logged_in_title
		self.input_selector = input_selector
		self.items_of_interest = items_of_interest
		self.login_required = login_required
		self.wait_for = wait_for
		self.homepage = homepage if homepage else self.url
		self.id = False
		self.company_name = None ## inferred company name

class SeleniumSetup(object):
	def __init__(
		self,
		## chromedriver path
		driver_path=Path(__file__).parent.joinpath('chromedriver').resolve(),
		## self explanatory
		cookies_file_path=Path(__file__).parent.joinpath('cookies.pkl').resolve(),
		local_user_prof_path="selenium"
	):
		self.driver_path = driver_path
		chrome_options = Options()
		chrome_options.add_argument("user-data-dir={}".format(local_user_prof_path))
		self.driver = webdriver.Chrome(
			executable_path=self.driver_path,
			options=chrome_options
		)



	def get_wait_object(self, seconds):
		return WebDriverWait(self.driver, seconds)

	def save_cookies(self):
		cookies = self.driver.get_cookies()
		pickle.dump(cookies, open(self.cookies_file_path, "wb"))

	def close_all(self):
		# close all open tabs
		if len(self.driver.window_handles) < 1:
			return

		for window_handle in self.driver.window_handles[:]:
			self.driver.switch_to.window(window_handle)
			self.driver.close()

	def quit(self):
		self.close_all()
		self.driver.quit()


	def login(self, website):
		username_box = self.driver.find_element_by_xpath(website.username_selector)
		username_box.send_keys(website.username)

		password_box = self.driver.find_element_by_xpath(website.password_selector)
		password_box.send_keys(website.password)

		login_button = self.driver.find_element_by_xpath(website.login_button_selector)
		login_button.click()

	def is_logged_in(self, website):

		elements = self.driver.find_elements_by_xpath(website.login_button_selector)
		if elements:
			print('not logged in')
			return False
		else:
			print('already logged in')
			return True


if __name__ == '__main__':
	pass
