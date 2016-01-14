import xmltodict
import json
import sys
import getopt
import requests


def usage():
    print """Usage:
    get-json-from-robot.py --xml=<output.xml> --pod=<pod_name> --installer=<installer>
    -x, --xml   xml file generated by robot test
    -p, --pod   POD name where the test come from
    -i, --installer   
    -h, --help  this message
    """
    sys.exit(2)


def populate_detail(test):
    detail = {}
    detail['test_name'] = test['@name']
    detail['test_status'] = test['status']
    detail['test_doc'] = test['doc']
    return detail


def parse_test(tests, details):
    try:
        for test in tests:
            details.append(populate_detail(test))
    except TypeError:
        # tests is not iterable
        details.append(populate_detail(tests))
    return details


def parse_suites(suites):
    data = {}
    details = []
    try:
        for suite in suites:
            data['details'] = parse_test(suite['test'], details)
    except TypeError:
        # suites is not iterable
        data['details'] = parse_test(suites['test'], details)
    return data


def send_results_to_mongo(payload):
    """
    todo: send json results to mongodb
    see:  https://wiki.opnfv.org/collection_of_test_results
    """
    server = '213.77.62.197'
    resource = 'http://' + server + '/results?project=ODL'
    #resource = 'http://' + server + '/results'
    #response = requests.post(resource, json=payload)
    response = requests.get(resource)
    print(response)
    print(response.text)

def main(argv):
    try:
        opts, args = getopt.getopt(argv, 'x:p:i:h', ['xml=', 'pod=', 'installer=', 'help'])
    except getopt.GetoptError:
        usage()

    for opt, arg in opts:
        if opt in ('-h', '--help'):
            usage()
        elif opt in ('-x', '--xml'):
            xml_file = arg
        elif opt in ('-p', '--pod'):
            pod = arg
        elif opt in ('-i', '--installer'):
            installer = arg
        else:
            usage()

    with open (xml_file, "r") as myfile:
        xml_input=myfile.read().replace('\n', '')

    # dictionary populated with data from xml file
    all_data = xmltodict.parse(xml_input)['robot']

    data = parse_suites(all_data['suite']['suite'])
    data['description'] = all_data['suite']['@name']
    data['version'] = all_data['@generator']
    data['test_project'] = "functest"
    data['case_name'] = "ODL"
    data['pod_name'] = pod
    data['installer'] =  installer

    print(json.dumps(data, indent=2))
    #send_results_to_mongo(data)

if __name__ == "__main__":
    main(sys.argv[1:])
