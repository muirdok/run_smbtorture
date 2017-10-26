import sys, getopt
import urllib.request, urllib.error
import json, base64
import configparser
###################################################################################Start of BINDINGs####################
class APIClient:
	def __init__(self, base_url):
		self.user = ''
		self.password = ''
		if not base_url.endswith('/'):
			base_url += '/'
		self.__url = base_url + 'index.php?/api/v2/'

	def send_get(self, uri):
		return self.__send_request('GET', uri, None)

	def send_post(self, uri, data):
		return self.__send_request('POST', uri, data)

	def __send_request(self, method, uri, data):
		url = self.__url + uri
		request = urllib.request.Request(url)
		if (method == 'POST'):
			request.data = bytes(json.dumps(data), 'utf-8')
		auth = str(
			base64.b64encode(
				bytes('%s:%s' % (self.user, self.password), 'utf-8')
			),
			'ascii'
		).strip()
		request.add_header('Authorization', 'Basic %s' % auth)
		request.add_header('Content-Type', 'application/json')

		e = None
		try:
			response = urllib.request.urlopen(request).read()
		except urllib.error.HTTPError as ex:
			response = ex.read()
			e = ex

		if response:
			result = json.loads(response.decode())
		else:
			result = {}

		if e != None:
			if result and 'error' in result:
				error = '"' + result['error'] + '"'
			else:
				error = 'No additional error message received'
			raise APIError('TestRail API returned HTTP %s (%s)' %
				(e.code, error))

		return result

class APIError(Exception):
	pass
###################################################################################END of BINDINGs######################

config = configparser.ConfigParser()
config.read('../settings.ini')
client = APIClient(config['connection']['railsurl'])
client.user = config['connection']['username']
client.password = config['connection']['password']

testrunid = config['testrun']['testrunid']
projectID = config['project']['projectid']
suite_id = config['suite']['suiteid']
section_id = config['section']['sectionid']

buildurl = config['jenkins']['buildurl']
version = config['nex']['version']

def add_case(title):
    testcase = {'title': title, 'type_id': 2, 'priority_id': 3, 'estimate': '10m', 'refs': 'null', 'custom_platform': 9}
    client.send_post('add_case/%s'%(section_id), testcase)

def main(argv):
   title = ''
   try:
      opts, args = getopt.getopt(argv,"h:t:",["titlte="])
   except getopt.GetoptError:
      print ('test.py -t <title>')
      sys.exit(2)
   for opt, arg in opts:
      if opt == '-h':
         print ('test.py -t <title>')
         sys.exit()
      elif opt in ("-t", "--title"):
         title = arg
   print ('new case title is: ', title)
# Create new case
   add_case(title)
   

if __name__ == "__main__":
   main(sys.argv[1:])
