import sys, getopt
import urllib.request, urllib.error
import json, base64
import configparser
#Result Codes:
#PASSED                                 = 1
#BLOCKED                                = 2
#UNTESTED                               = 3
#RETEST                                 = 4
#FAILED                                 = 5
#FAILEDR - Regression                   = 6
#FAILEDA - failed_auto                  = 7
#FAILEDAR- failed_auto_regression       = 8

################################################################################Start of BINDINGs####################
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
################################################################################END of BINDINGs######################
config = configparser.ConfigParser()
config.read('settings.ini')
client = APIClient(config['connection']['railsurl'])
client.user = config['connection']['username']
client.password = config['connection']['password']
testrunid = config['testrun']['testrunid']
buildurl = config['jenkins']['buildurl']
version = config['nex']['version']

def add_tcase_resuts(testid,result,version):
    client.send_post('add_result/%s' % (testid),{'status_id': result, 'comment': 'Added from Jenkins: %s' % (buildurl),'version': version})

def get_tests(run_id):
    tcases = client.send_get('get_tests/%s' % (run_id))
    return tcases

def get_testid(tcases, title):
    for p in tcases:
        if p['title']==title:
            testid = p['id']
            return testid

def add_tcase_resuts(testid,result,version,comment):
    client.send_post('add_result/%s' % (testid),{'status_id': result, 'comment': 'From script: %s' % (comment),'version': version})

def main(argv):
    title = ''
    result = ''
    comment = ''
    try:
       opts, args = getopt.getopt(argv,"h:t:r:c:",["title=", "result=","comment="])
    except getopt.GetoptError:
       print ('addresult_by_title.py -t <title> -r <result> -c <comment>')
       sys.exit(2)
    for opt, arg in opts:
       if opt == '-h':
          print ('addresult_by_title.py -t <titile> -r <result> -c <comment>')
          sys.exit()
       elif opt in ("-t", "--title"):
          title = arg
       elif opt in ("-r", "--result"):
          result = arg
       elif opt in ("-c", "--comment"):
          comment = arg

    if   result == 'PASSED': result = 1
    elif result == 'BLOCKED': result = 2
    elif result == 'UNTESTED': result = 3
    elif result == 'RETEST': result = 4
    elif result == 'FAILED': result = 5
    elif result == 'FAILEDR': result = 6
    elif result == 'FAILEDA': result = 7
    elif result == 'FAILEDAR': result = 8

    print ('Test title is: ', title)
    print ('Result: ', result)
    print ('Comment: ', comment)
    add_tcase_resuts(get_testid(get_tests(testrunid),title),result,version,comment)
#    print (get_testid(get_tests(testrunid),title),result,version)
    
if __name__ == "__main__":
    main(sys.argv[1:])
