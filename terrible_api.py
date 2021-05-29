from __future__ import print_function
import os.path
import re
from googleapiclient.discovery import build
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
# from googleapiclient.errors import RefreshError
from google.api_core import exceptions as google_exceptions
from google.auth.exceptions import RefreshError, UserAccessTokenError

# If modifying these scopes, delete the file token.json.
# SCOPES = ['https://www.googleapis.com/auth/documents.readonly']

# The ID of a sample document.
# DOCUMENT_IDS = {'lesson_plan': '1mdCe_ObVFtk8O-qrHnf9HsKjUo--9yCfoB30UuQ-qq8',
#                 'sales_quote': '1dPxhYR_N2MKMX3apR_CHymlXuzkUm5bin-744YehNRQ'
# }


class GoogleDoc(object):
	def __init__(self, id, cred_file_path, scopes, template=True, testing=False):
		self.doc_id = id
		self.scopes = scopes
		self.cred_file_path = cred_file_path
		self.template = template
		self.testing = testing
		self.creds = self.cred_setup(cred_file_path)
		self.service = self.get_service()
		self.document = self.get_document()

	def delete(self):

		print('deleting document')
		service = self.get_service('drive', 'v3')
		response = service.files().delete(fileId=self.doc_id).execute()
		return response

	## returns list containing index start and end for a given term
	def get_term_range(self, term, id=None, regex=None):
		document = self.get_document_structure(id)
		term_range = [0,1]
		def item_iterator(itm):
			if type(itm) is dict:
				if 'textRun' in itm.keys() and term in itm['textRun']['content']:
					return {'range':[itm['startIndex'], itm['endIndex']], 'content': itm['textRun']['content']}
				else:
					for k,v in itm.items():
						found = item_iterator(v)
						if found is not None:
							return found

			elif type(itm) is list:
				for x in itm:
					found = item_iterator(x)
					if found is not None:
						return found


		for item in document['body']['content']:
			term_info = item_iterator(item)
			if term_info:
				term_range = term_info['range']
				break

		term_range[1] -= 1
		if regex:
			## use regex to get index of match start and match end

			pattern = re.compile(regex)
			match = pattern.search(term_info['content'])
			if match:
				start = match.start() + term_range[0]
				end = (match.end() - match.start()) + start
				# end = match.end() + term_range[0]
				term_range = [start, end]


		return term_range

	def cred_setup(self, cred_path=None):
		cred_path = cred_path if cred_path else self.cred_file_path
		creds = None
		try:

			if os.path.exists('token.json'):
				creds = Credentials.from_authorized_user_file('token.json', self.scopes)
			# If there are no (valid) credentials available, let the user log in.

			if not creds or not creds.valid:
				if creds and creds.expired and creds.refresh_token:
					creds.refresh(Request())
				else:
					flow = InstalledAppFlow.from_client_secrets_file(
						cred_path, self.scopes)
					creds = flow.run_local_server(port=0)
				# Save the credentials for the next run
				with open('token.json', 'w') as token:
					token.write(creds.to_json())

			return creds

		except RefreshError as err:

			print('\n-------------\nError using existing token (maybe it expired).\n-------------\n')
			# attempt to reauthenticate
			return self.re_auth(cred_path)


	def get_service(self, api='docs', version='v1', creds=None):
		creds = creds if creds else self.cred_setup(self.cred_file_path)
		return build(api, version, credentials=creds)


	def get_document(self, id=None):
		id = self.doc_id if not id else id
		service = self.get_service('docs', 'v1')
		document = service.documents().get(documentId=id).execute()
		return document

	def re_auth(self, cred_path):
		print('\n-------------\nAttempting reauth\n-------------\n')
		os.remove("token.json")
		flow = InstalledAppFlow.from_client_secrets_file(cred_path, self.scopes)
		creds = flow.run_local_server(port=0)
		# Save the credentials for the next run
		with open('token.json', 'w') as token:
			token.write(creds.to_json())

		return creds


	def create_copy(self, title='Copy of Account Plan Template', id=None):
		id = self.doc_id if not id else id
		service = self.get_service('drive', 'v3')
		response = service.files().copy(fileId=id, body={'name':title}).execute()
		return response

	def get_document_structure(self, id=None):
		"""
		returns the structure of a given document as a dictionary
		"""
		id = self.doc_id if not id else id
		document = self.get_document(id)
		return document

	def get_named_ranges(self, id=None):
		"""
		returns all named ranges in a given document
		"""
		id = self.doc_id if not id else id
		document = self.get_document(id)
		named_ranges = document.get('namedRanges', {})
		return named_ranges

	def print_named_ranges(self, id=None):
		"""
		prints all named ranges in a given document
		"""
		named_ranges = self.get_named_ranges(id)
		if named_ranges:
			print('---------------\nprinting named ranges: ')
			for k,v in named_ranges.items():
				print("\n", k)
				print(v, "\n")
		else:
			print('no named ranges in current document')

	def get_title(self):
		"""
		returns the title of a given document.
		"""
		document = self.get_document()
		return document.get('title')

	def create_named_ranges(self, new_requests):
		document = self.get_document()
		requests = []
		for item in new_requests:

			range = {"startIndex": item['start'], "endIndex": item['end']}

			requests.append({
				'createNamedRange': {
					'name': item['name'],
					'range': range
				}
			})

		if requests:

			body = {
				'requests': requests,
				'writeControl': {
					'requiredRevisionId': document.get('revisionId')
				}
			}
			# service = self.get_service()
			result = self.service.documents().batchUpdate(documentId=self.doc_id, body=body).execute()
			print('created named range: ', result)


	def delete_named_range(self, range_name):

		"""deletes existing named ranges."""

		# Fetch the document to determine the current indexes of the named ranges.
		# document = self.get_document()

		# Find the matching named ranges.
		named_range_list = self.document.get('namedRanges', {}).get(range_name)
		if not named_range_list:
			raise Exception('The named range is no longer present in the document.')

		# Determine all the ranges to be removed
		requests = []
		requests.append({
			'deleteNamedRange': {
				'name': range_name
			}
		})

		body = {
			'requests': requests,
			'writeControl': {
				'requiredRevisionId': self.document.get('revisionId')
			}
		}
		# service = self.get_service()
		result = self.service.documents().batchUpdate(documentId=self.doc_id, body=body).execute()
		print('deleted named range: ', result)


	def replace_named_range_content(self, requests=[]):
		"""Replaces the text in existing named ranges."""
		document = self.get_document()
		for item,index in zip(requests,range(len(requests))):
			requests[index] = {
				'replaceNamedRangeContent':{
					'text': item['text'],
					'namedRangeName': item['name']
				}
			}

		if requests:

			# Make a batchUpdate request to apply the changes, ensuring the document
			# hasn't changed since we fetched it.
			body = {
				'requests': requests,
				'writeControl': {
					'requiredRevisionId': document.get('revisionId')
				}
			}
			# service = self.get_service()
			response = self.service.documents().batchUpdate(documentId=self.doc_id, body=body).execute()
			print('replaced content in named ranges: ', response)

	def replace_named_range_old(self, range_name, new_text):

		"""Replaces the text in existing named ranges."""

		# Determine the length of the replacement text, as UTF-16 code units.
		# https://developers.google.com/docs/api/concepts/structure#start_and_end_index
		new_text_len = len(new_text.encode('utf-16-le'))/2

		# Fetch the document to determine the current indexes of the named ranges.
		# document = self.get_document()

		# Find the matching named ranges.
		named_range_list = self.document.get('namedRanges', {}).get(range_name)
		if not named_range_list:
			raise Exception('The named range is no longer present in the document.')

		# Determine all the ranges of text to be removed, and at which indices the
		# replacement text should be inserted.
		all_ranges = []
		insert_at = {}

		for named_range in named_range_list.get('namedRanges'):
			ranges = named_range.get('ranges')
			all_ranges.extend(ranges)
			# Most named ranges only contain one range of text, but it's possible
			# for it to be split into multiple ranges by user edits in the document.
			# The replacement text should only be inserted at the start of the first
			# range.
			insert_at[ranges[0].get('startIndex')] = True

		# Sort the list of ranges by startIndex, in descending order.
		all_ranges.sort(key=lambda r: r.get('startIndex'), reverse=True)

		# Create a sequence of requests for each range.
		requests = []
		for r in all_ranges:
			# Delete all the content in the existing range.
			requests.append({
				'deleteContentRange': {
					'range': r
				}
			})

			segment_id = r.get('segmentId')
			start = r.get('startIndex')
			if insert_at[start]:
				# Insert the replacement text.
				requests.append({
					'insertText': {
						'location': {
							'segmentId': segment_id,
							'index': start
						},
						'text': new_text
					}
				})
				# Re-create the named range on the new text.
				requests.append({
					'createNamedRange': {
						'name': range_name,
						'range': {
							'segmentId': segment_id,
							'startIndex': start,
							'endIndex': start + new_text_len
						}
					}
				})

		# Make a batchUpdate request to apply the changes, ensuring the document
		# hasn't changed since we fetched it.
		body = {
			'requests': requests,
			'writeControl': {
				'requiredRevisionId': self.document.get('revisionId')
			}
		}

		# service = self.get_service()
		result = self.service.documents().batchUpdate(documentId=self.doc_id, body=body).execute()

		print(result)



if __name__ == '__main__':
	DOCUMENT_IDS = {'lesson_plan': '1mdCe_ObVFtk8O-qrHnf9HsKjUo--9yCfoB30UuQ-qq8',
					'sales_quote': '1dPxhYR_N2MKMX3apR_CHymlXuzkUm5bin-744YehNRQ'
	}
	google_doc = GoogleDoc(DOCUMENT_IDS['sales_quote'], ['https://www.googleapis.com/auth/documents.readonly'],
		os.environ['GOOGLE_DOCS_CREDS']
	)

	google_doc.get_title()
