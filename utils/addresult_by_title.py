import base64
import configparser
import getopt
import json
import sys
import urllib.error
import urllib.request


# Result Codes:
# PASSED                                 = 1
# BLOCKED                                = 2
# UNTESTED                               = 3
# RETEST                                 = 4
# FAILED                                 = 5
# FAILEDR - Regression                   = 6
# FAILEDA - failed_auto                  = 7
# FAILEDAR- failed_auto_regression       = 8
# on RAILS
# 1 - passed
# 2 - blocked
# 4 - retest
# 5 - Failed - Known Issue
# 6 - Failed - Regression
# 7 - Test Excepti..Known Issue
# 8 - Test Excepti.. Regression


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
        if method == 'POST':
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

        if e is not None:
            if result and 'error' in result:
                error = '"' + result['error'] + '"'
            else:
                error = 'No additional error message received'
            raise APIError('TestRail API returned HTTP %s (%s)' %
                           (e.code, error))

        return result


class APIError(Exception):
    pass


config = configparser.ConfigParser()
config.read('settings.ini')

client = APIClient(config['connection']['railsurl'])
client.user = config['connection']['username']
client.password = config['connection']['password']

project_id = config['project']['project_id']
suite_id = config['suite']['suite_id']

test_run_previous = config['testrun']['test_run_previous']
test_run_id = config['testrun']['test_run_id']

buildurl = config['jenkins']['buildurl']
version = config['nex']['version']

def add_case_result(run_id, case_id, result, vers, comment):
    client.send_post('add_result_for_case/%s/%s' % (run_id, case_id),
                     {'status_id': result, 'comment': 'From script: %s' % comment, 'version': vers})
					 
def get_caseid_from_suite (project_id, suite_id, title):
    cases = client.send_get('get_cases/%s&suite_id=%s' % (project_id, suite_id))
    for p in cases:
        if p['title'] == title:
            case_id = p['id']
            return case_id					 

def get_test_result(run_id, case_id):
    offset = 1
    madick = client.send_get('get_results_for_case/%s/%s&limit=%s' % (run_id, case_id, offset))[0]
    return madick["status_id"]        


def main(argv):
    title = ''
    result = ''
    comment = ''
    try:
        opts, args = getopt.getopt(argv, "h:t:r:c:", ["title=", "result=", "comment="])
    except getopt.GetoptError:
        print('addresult_by_title.py -t <title> -r <result> -c <comment>')
        sys.exit(2)
    for opt, arg in opts:
        if opt == '-h':
            print('addresult_by_title.py -t <titile> -r <result> -c <comment>')
            sys.exit()
        elif opt in ("-t", "--title"):
            title = arg
        elif opt in ("-r", "--result"):
            result = arg
        elif opt in ("-c", "--comment"):
            comment = arg

    result_id = int(0)            

    if result == 'PASSED':
        result_id = 1
    elif result == 'BLOCKED':
        result_id = 2
    elif result == 'UNTESTED':
        result_id = 3
    elif result == 'RETEST':
        result_id = 4
    elif result == 'FAILED':
        result_id = 5
    elif result == 'FAILEDR':
        result_id = 6
    elif result == 'FAILEDA':
        result_id = 7
    elif result == 'FAILEDAR':
        result_id = 8
    
    case_id = get_caseid_from_suite(project_id, suite_id, title)
    last_result = get_test_result(test_run_previous, case_id)

    if int(last_result) == 1 and result_id >= 5:
        result_id = 8
        add_case_result(test_run_id, case_id, result_id, version, comment)
    else:
        add_case_result(test_run_id, case_id, result_id, version, comment)

if __name__ == "__main__":
    main(sys.argv[1:])
