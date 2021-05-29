import asyncio, os, re, time
import tkinter as tk
from tkinter import IntVar, StringVar, ttk
from functools import partial

from selenium.common.exceptions import TimeoutException
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
# from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from terrible_api import GoogleDoc
from assets import PageItem, SeleniumSetup, Website

# TODO:
## 1. add captcha support
## 2. put site settings in separate file (json)
## 3. add logging
## 4. prevent duplicate file creation (based on w/e support gdocs has)


class App(tk.Tk):
	def __init__(self, driver_object, document, websites=[], title="KYLES HARDCORE PORN HACK PWNER"):
		self.selenium_object = driver_object
		self.driver = driver_object.driver # for convenience
		self.websites = websites
		self.document = document
		super().__init__()
		self.columnconfigure(0, weight=1)
		self.columnconfigure(1, weight=1)
		self.title(title)
		self.setup_stringvars()
		self.create_widgets()
		self._configure_bindings()
		self.geometry("800x500")
		self.startup()

	def setup_stringvars(self):
		for website in self.websites:
			for item in website.items_of_interest:
				item.value = StringVar()

	def _configure_bindings(self):
		# self.bind('<t>', lambda event: asyncio.ensure_future(self.spam(event)))
		# self.bind('<x>', lambda event: asyncio.ensure_future(self.exit()))
		self.bind('<Return>', lambda event: asyncio.ensure_future(self.search_all()))

	def create_widgets(self):

		self.mainframe = tk.PanedWindow(self, orient="horizontal", width=800, sashpad=2, sashrelief="ridge")
		self.mainframe.grid(column=0, row=0)
		self.mainframe.pack(fill='both', expand=True)

		self.left_frame = ttk.Frame(self.mainframe, padding="10 10")
		self.left_frame.grid(column=0, row=0, sticky=("NSEW"))

		self.right_frame = ttk.Frame(self.mainframe, padding="10 10")
		self.right_frame.grid(column=1, row=0, sticky=("NSEW"))

		self.mainframe.add(self.left_frame)
		self.mainframe.add(self.right_frame)
		self.mainframe.columnconfigure(1, weight=1)

		# left frame
		self.left_frame.rowconfigure(0, weight=0)
		self.left_frame.rowconfigure(1, weight=1)
		self.left_frame.rowconfigure(2, weight=1)

		self.left_frame.columnconfigure(0, weight=1)
		self.left_frame.columnconfigure(1, weight=1)
		self.left_frame.columnconfigure(2, weight=1)

		### search functionality
		self.search_term = StringVar()
		ttk.Entry(self.left_frame, textvariable=self.search_term).grid(row=0, column=0, sticky=("NW"))
		ttk.Button(self.left_frame, text='Search', command=lambda: asyncio.ensure_future(self.search_all())).grid(row=0, column=1, sticky=("NW"))

		### company name
		self.company_name_var = StringVar()
		self.company_name_var.set('Enter Company Name')
		# ttk.Label(self.left_frame, text='Company:').grid(row=1, column=0, sticky=("NW"))
		ttk.Entry(self.left_frame, textvariable=self.company_name_var).grid(row=1, column=0, sticky=("NW"))
		self.same_as_search = IntVar()
		ttk.Checkbutton(self.left_frame, text='Same as Search', variable=self.same_as_search, command=self.set_company_name).grid(row=1, column=1, sticky=("NW"))

		### exit button
		ttk.Button(self.left_frame, text='Exit', underline=1, command=lambda: asyncio.ensure_future(self.exit())).grid(row=20, sticky=("SW"))

		### google doc test area
		# self.named_range_name = StringVar()
		# self.named_range_start_index = StringVar()
		# self.named_range_end_index = StringVar()
		#
		# self.named_range_value = StringVar()
		# self.named_range_delete = StringVar()
		#
		# ttk.Separator(self.left_frame, orient='horizontal').grid(row=2, column=0, sticky=("EW"), columnspan=3, padx=5, pady=5)
		#
		# ttk.Label(self.left_frame, text='named range').grid(row=3, column=0, sticky=("NW"))
		# ttk.Entry(self.left_frame, textvariable=self.named_range_name).grid(row=3, column=1, sticky=("NW"))
		# ttk.Button(self.left_frame, text='create', command=lambda: asyncio.ensure_future(self.create_range())).grid(row=3, column=2, sticky=("NW"))
		#
		# ttk.Label(self.left_frame, text='index').grid(row=4, column=0, sticky=("NW"))
		# ttk.Entry(self.left_frame, textvariable=self.named_range_start_index).grid(row=4, column=1, sticky=("W"))
		# ttk.Entry(self.left_frame, textvariable=self.named_range_end_index).grid(row=4, column=2, sticky=("W"))
		#
		# ttk.Label(self.left_frame, text='update value').grid(row=5, column=0, sticky=("NW"))
		# ttk.Entry(self.left_frame, textvariable=self.named_range_value).grid(row=5, column=1, sticky=("NW"))
		#
		#ttk.Label(self.left_frame, text='delete range (name)').grid(row=6, column=0, sticky=("NW"))
		#ttk.Entry(self.left_frame, textvariable=self.named_range_delete).grid(row=6, column=1, sticky=("NW"))
		#ttk.Button(self.left_frame, text='delete', command=self.delete_range).grid(row=6, column=2, sticky=("NW"))

		# ttk.Button(self.left_frame, text='save', command=lambda: asyncio.ensure_future(self.change_range_val())).grid(row=5, column=2, sticky=("NW"))

		## print functions
		#ttk.Button(self.left_frame, text='print all', command=self.print_googledoc_info).grid(row=7, column=2, sticky=("NW"))
		#ttk.Button(self.left_frame, text='print named', command=self.document.print_named_ranges).grid(row=8, column=2, sticky=("NW"))

		# right frame
		self.right_frame.columnconfigure(0, weight=1)
		self.right_frame.columnconfigure(1, weight=1, pad=5)
		self.right_frame.columnconfigure(2, weight=1)

		ttk.Button(self.right_frame, text='Setup', command=self.startup).grid(row=0, column=0, sticky=("NE"), padx=5)
		# ttk.Button(self.right_frame, text='Window Handles', command=lambda: asyncio.ensure_future(self.print_stuff())).grid(row=2, column=1, sticky=("SE"))
		# self.right_frame.columnconfigure(4, weight=0, minsize=50)

		for website in self.websites:
			index = self.websites.index(website) + 1
			self.right_frame.rowconfigure(index, weight=1)

			frame = ttk.Frame(self.right_frame, relief="ridge", borderwidth=2)
			frame.grid(row=index, column=0, sticky=("NSEW"), pady=5)
			ttk.Label(frame, text=website.name, underline=0).grid(row=0, column=0, sticky=("NW"))
			retry_search = partial(lambda website: asyncio.ensure_future(self.search(website)), website)

			ttk.Button(frame, text='Retry', command=retry_search).grid(row=0, column=1, sticky=("NE"))
			ttk.Separator(frame, orient='horizontal').grid(row=1, column=0, sticky=("EW"), columnspan=3, padx=5, pady=5)

			frame.columnconfigure(0, weight=0, minsize=125)
			frame.columnconfigure(1, weight=2)

			cols,i = self.right_frame.grid_size()

			for item in [x for x in website.items_of_interest if x.of_interest]:
				ttk.Label(frame, text=item.label).grid(row=i, column=0, sticky=("W"))
				ttk.Entry(frame, textvariable=item.value).grid(row=i, column=1, sticky=("EW"), columnspan=2)
				copy_copy = partial(lambda val: asyncio.ensure_future(self.copy_to_clipboard(val)), item.value)

				ttk.Button(frame, text='Copy', command=copy_copy).grid(row=i, column=3, sticky=("NE"))
				i += 1
				cols,i = frame.grid_size()

		self.footer_frame = ttk.Frame(self.right_frame,borderwidth=2)
		self.footer_frame.grid(row=20, column=0, sticky=("NSEW"))
		self.footer_frame.columnconfigure(0, weight=1)
		self.footer_frame.columnconfigure(1, weight=1)
		self.footer_frame.columnconfigure(2, weight=1)

		ttk.Label(self.footer_frame, text="Google Document").grid(row=0, column=0, sticky=("NW"))
		self.google_doc_url = StringVar()

		url_entry = ttk.Entry(self.footer_frame, textvariable=self.google_doc_url, state="readonly")

		url_entry.grid(row=1, column=0, sticky=("SEW"), columnspan=3)
		self.google_doc_url.set("https://docs.google.com/")
		ttk.Button(self.footer_frame, text='Copy', command=lambda: asyncio.ensure_future(self.copy_to_clipboard(self.google_doc_url))).grid(row=1, column=3, sticky=("SE"))

		ttk.Separator(self.footer_frame, orient='horizontal').grid(row=2, column=0, sticky=("EW"), columnspan=4, padx=5, pady=5)

		self.open_doc_new_tab = IntVar()
		self.is_test_document = IntVar()

		self.is_test_document.set(0)

		ttk.Checkbutton(self.footer_frame, text='Open in New Tab', variable=self.open_doc_new_tab).grid(row=3, column=0, sticky=("SW"))
		# ttk.Checkbutton(self.footer_frame, text='Test Document?', variable=self.is_test_document).grid(row=5, column=0, sticky=("SW"))
		ttk.Button(self.footer_frame, text='Create Copy', underline=0, command=self.create_copy).grid(row=4, column=0, sticky=("SW"))
		# ttk.Button(self.footer_frame, text='Setup Named Ranges', underline=0, command=self.setup_named_ranges).grid(row=2, column=2, sticky=("NE"))
		ttk.Button(self.footer_frame, text='Upload', underline=0, command=self.upload_to_doc).grid(row=4, column=3, sticky=("SE"))




	def upload_to_doc(self):

		if self.document.template:
			self.create_copy()

		if not self.company_name_var.get():
			self.set_company_name()

		requests = [{'name':'company_name', 'text': self.company_name_var.get()}]

		for website in self.websites:
			for item in website.items_of_interest:
				if item.of_interest and item.value.get():
					requests.append({'name':item.range_name, 'text':item.value.get()})

		self.document.replace_named_range_content(requests)

	def setup_named_ranges(self):
		requests = []
		term_range = self.document.get_term_range('company_name', regex="company\_name")
		named_ranges = self.document.get_named_ranges()

		if 'company_name' not in named_ranges.keys():
			requests.append({'name':'company_name', 'start':term_range[0], 'end':term_range[1]})

		for website in self.websites:
			for item in website.items_of_interest:
				if item.of_interest and item.range_name not in named_ranges.keys():
					requests.append({'name': item.range_name, 'start': item.start, 'end': item.end})


		self.document.create_named_ranges(requests)
		time.sleep(0.5)


	def set_company_name(self, name=None):
		company_name = ''

		if name:
			company_name = name

		elif self.same_as_search.get() and self.search_term.get():
			company_name = self.search_term.get().title()

		else:
			inferred_company_names = [website.company_name for website in self.websites if website.company_name]
			if inferred_company_names:
				company_name = inferred_company_names[0]
				## TODO: compare the list of names and if they are similar try to infer correct name based on commonalities
				## example: 'acretoo' vs. 'accreto' vs. 'acretto' would coerce to 'acreto'

		if not company_name:
			company_name = self.search_term.get()

		self.company_name_var.set(company_name)



	def create_copy(self):
		self.setup_named_ranges()
		if not self.company_name_var.get():
			self.set_company_name()

		company = self.company_name_var.get()
		title = "{} Account Plan".format(company) if company else "Copy of Account Template"
		response = self.document.create_copy(title)
		cred_file, scopes = self.document.cred_file_path, self.document.scopes
		self.document = GoogleDoc(response['id'], cred_file, scopes, template=False, testing=bool(self.is_test_document.get()))

		url = "https://docs.google.com/document/d/{}/edit".format(response['id'])
		if self.open_doc_new_tab.get():
			self.driver.execute_script("window.open('{}', '{}');".format(url, company))

		self.google_doc_url.set(url)
		print('Created copy. Response:\n', response)


	async def reset(self):
		# iterate through websites and return to home page
		# close any extra tabs
		pass


	async def copy_to_clipboard(self, item):
		self.clipboard_clear()
		self.clipboard_append(item.get())


	def print_googledoc_info(self):
		print('\nprinting document:\n----------------------\n', self.document.get_document_structure(), '\n----------------------\n')

	def delete_range(self):
		self.document.delete_named_range(self.named_range_delete.get())

	async def print_stuff(self):
		print('items:\n')
		for website in self.websites:
			print("{} :{}".format(website.name, website.items_of_interest))

	async def search_all(self):
		await asyncio.sleep(0.5)
		## iterate through tabs and enter search term
		## TODO: add captcha detection that pauses script if found
		for website in self.websites:
			await self.search(website)

	async def search(self, website):
		if not self.search_term.get():
			return

		search_time = 15
		wait = self.selenium_object.get_wait_object(search_time)

		# wait = WebDriverWait(self.driver, search_time)

		self.driver.switch_to.window(website.id)

		if self.driver.current_url != website.homepage:
			print('\nreturning to homepage')
			self.driver.get(website.url)
			wait.until(EC.element_to_be_clickable((By.XPATH, website.input_selector)))

		input_box = self.driver.find_element_by_xpath(website.input_selector)

		input_box.click()
		input_box.clear()
		input_box.click()
		input_box.send_keys(self.search_term.get())
		input_box.send_keys(Keys.ENTER)

		try:
			if website.wait_for:
				element = wait.until(EC.element_to_be_clickable((By.XPATH, website.wait_for)))

			for item in website.items_of_interest:
				wait.until(EC.element_to_be_clickable((By.XPATH, item.wait_for)))
				ele = self.driver.find_element_by_xpath(item.selector)
				if item.inferred_selector:
					website.company_name = self.driver.find_element_by_xpath(item.inferred_selector).text

				if item.of_interest:
					val = ele.get_attribute("href") if item.is_link else ele.text
					if website.name is "linkedin" and item.label is "headcount":
						m = re.findall(r"\d+(?=\semployee)", val)
						val = m[0]

					item.value.set(val)

				if item.is_link:
					href = ele.get_attribute("href")
					self.driver.get(href)

		except TimeoutException as e:
			print("unable to locate element in under {} seconds".format(search_time))

			# TODO: add popup dialog asking user if they would like to retry search

	async def spam(self, event):
		await self.do_something()
		await asyncio.sleep(2)
		print('%s executed!' % self.spam.__name__)


	def startup(self):
		try:
			for website in self.websites:
				if not website.id:
					if self.websites.index(website) != 0:
						self.driver.execute_script("window.open('{}', '{}');".format(website.url, website.name))
						self.driver.switch_to.window(self.driver.window_handles[-1])

					else:
						self.driver.get(website.url)

					website.id = self.driver.current_window_handle

				if website.login_required:
					self.driver.switch_to.window(website.id)
					if not self.selenium_object.is_logged_in(website):
						self.selenium_object.login(website)


		except Exception as e:
			print(str(e))
			print("Error opening URL for {}".format(website.name))

	async def do_something(self):
		print('%s executed!' % self.do_something.__name__)

	async def exit(self):
		print('Exiting')

		if self.document.testing and not self.document.template:
			self.document.delete()

		self.selenium_object.quit()
		self.destroy()

async def run_tk(root):
	try:
		while True:
			root.update()
			await asyncio.sleep(.01)
	except tk.TclError as e:
		if "application has been destroyed" not in e.args[0]:
			raise

if __name__ == '__main__':


	acct_template_doc = GoogleDoc(os.environ['ACCT_TEMPLATE_DOC_ID'], os.environ['GOOGLE_DOCS_CREDS'], scopes=['https://www.googleapis.com/auth/documents', 'https://www.googleapis.com/auth/drive'])
	websites = []

	google = Website("google", "https://www.google.com/", input_selector="//input[@name='q' and @type='text' and @title='Search']")
	google.items_of_interest = [
		PageItem(label="website", index=acct_template_doc.get_term_range("acct_site"),
			selector="//div[@id='search']//div[@class='g']//link[@rel='prerender']",
			wait_for="//div[@id='result-stats']", of_interest=True, is_link=True,
			range_name="acct_site"
		),
	]

	websites.append(google)

	linkedn = Website("linkedin", "https://www.linkedin.com/login",
		os.environ['LINKEDN_USERNAME'], os.environ['LINKEDN_PASSWORD'],
		username_selector="//form[@class='login__form']//input[@id='username' and @type='text']",
		password_selector="//form[@class='login__form']//input[@type='password']",
		login_button_selector="//form[@class='login__form']//button[@type='submit'][//text()='Sign in']",
		login_required=True, input_selector="//div[@id='global-nav-search']//input[@aria-label='Search' and @role='combobox']",
		wait_for="//div[@class='search-results-container']", homepage="https://www.linkedin.com/feed/"
	)

	linkedn.items_of_interest = [
		PageItem(label="first_search_link", index=acct_template_doc.get_term_range("linkedin_site"),
			selector="//div[@class='search-results-container']//a[@class='app-aware-link']",
			wait_for="//div[@class='search-results-container']", of_interest=True, is_link=True,
			range_name="linkedin_site"

		),
		PageItem(label="headcount", index=acct_template_doc.get_term_range("hc_var", regex="hc\_var"), of_interest=True,
			selector="//main[@id='main']//section[contains(@class, 'org-top-card')]//*[text()[contains(., 'employee')]]",
			wait_for="//div[@id='org-right-rail']//*[text()='Pages people also viewed']",
			inferred_selector="//span[@dir='ltr']", range_name="hc_var"
		)
	]
	websites.append(linkedn)

	crunchbase = Website("crunchbase", "https://www.crunchbase.com/",
		input_selector="//form//input[@type='search']",
		wait_for="//h1[text()[contains(., 'Search Companies')]]"
	)

	crunchbase.items_of_interest = [
		PageItem(label="company_link", wait_for="//grid-column-header[@data-columnid='identifier']",
			selector="//grid-row[1]//grid-cell[@data-columnid='identifier']//a[@role='link']",
			is_link=True
		),
		PageItem(label="location", of_interest=True, index=acct_template_doc.get_term_range("location_var"),
			selector="//section-card[//*[@class='section-title' and text()='About']]//fields-card//label-with-icon//field-formatter//span",
			wait_for="//span[@class='tab-label' and text()='Summary']",
			inferred_selector="//div[@class='identifier-nav']//span[@class='profile-name']",
			range_name="location_var"
		),
		PageItem(label="funding", of_interest=True, index=acct_template_doc.get_term_range("funding_var", regex="funding\_var"),
			selector="//div[@class='info'][//span[text()[contains(., 'Total Funding')]]]//field-formatter",
			wait_for="//span[@class='tab-label' and text()='Summary']", range_name="funding_var"
		)
	]
	websites.append(crunchbase)

	salesforce = Website("salesforce", "https://www.salesforce.com/",
		input_selector='', wait_for=''
	)
	salesforce.items_of_interest = [
		PageItem(label="SFDC", index=acct_template_doc.get_term_range("sfdc_var"),
			of_interest=True, selector="", wait_for="",
			range_name="sfdc_var"
		)
	]

	selenium_object = SeleniumSetup()
	app = App(selenium_object, websites=websites, document=acct_template_doc)
	asyncio.get_event_loop().run_until_complete(run_tk(app))
