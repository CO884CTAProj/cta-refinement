""" Provides the URL routes for the REST API implementation.
"""
from flask import jsonify, abort, request, Blueprint, session, make_response,Response
from settings import EXAMPLES_DIRECTORY, DBM_DIRECTORY
import os, sys
import json
sys.path.append(DBM_DIRECTORY)
from CtaWebFunctions import *


REFINER_API = Blueprint('api', __name__)

def get_blueprint():
    """Return the API blueprint for the main app module"""
    return REFINER_API

@REFINER_API.route('/api/cta/<string:cta_name>', methods=['GET','POST','PUT','DELETE'])
def cta_functions(cta_name):  # noqa: E501
    """Adds/Removes/Updates/Gets a CTA from the session

    Adds/Removes/Updates/Gets a CTA to the session # noqa: E501

    :param CTA: CTA to add/update/delete/get
    :type CTA: dict | bytes

    :rtype: None
    """
    if request.method == 'GET':
        try:
            cta = get_cta(cta_name)
            return json.dumps(cta), 200
        except:
            return handle_404_error(404)

    if request.method == 'POST':
        cta = request.get_json()
        name = cta["name"]
        definition = cta["CTA"]

        if cta_present(name):
            return "A CTA with the name " + name + " already exists in this session.", 400
        else:
            append_cta(name, definition)
            return json.dumps(session["CTA List"]), 200

    if request.method == 'PUT':
        try:
            new_cta = request.get_json()
            name = new_cta["name"]
            definition = new_cta["CTA"]

            if cta_present(cta_name):
                cta_obj = get_cta(cta_name)
                cta_obj["CTA"] = definition
		session.modified = True
                return json.dumps(session["CTA List"]), 200
            else:
                return handle_404_error(404)
        except:
            return handle_400_error(400)

    if request.method == 'DELETE':
        try:
            for cta in session["CTA List"]:
                if cta["name"] == cta_name:
                    session["CTA List"].remove(cta)
		    session.modified = True
                    return json.dumps(session["CTA List"]), 200
                else:
                    return handle_404_error(404)
        except:
            return handle_400_error(400)


@REFINER_API.route('/api/grammar', methods=['GET'])
def get_grammar():  # noqa: E501
    """Gets CTA grammar rules.

    This will return the grammar rules for specifying CTAs  # noqa: E501

    :rtype: object
    """
    try:
        f = open(DBM_DIRECTORY+"grammar","r")
        grammar = f.readlines()
        return jsonify(grammar_rules=grammar), 200
    except:
        return handle_404_error(404)

@REFINER_API.route('/api/sample-scripts/<string:sample_name>', methods=['GET'])
def get_sample(sample_name):  # noqa: E501
    """returns a specified sample script

    By passing in the specified sample script name you are able to get a sample script  # noqa: E501

    :param sample_name:
    :type sample_name: str

    :rtype: object
    """
    try:
        f = open(EXAMPLES_DIRECTORY+sample_name,"r")
        example = f.readlines()
        return jsonify(name=sample_name,sample_script=example), 200
    except:
        return handle_404_error(404)

@REFINER_API.route('/api/sample-scripts', methods=['GET'])
def get_samples():  # noqa: E501
    """returns a list of available sample scripts

    Returns a list of available sample scripts which can be passed as a parameter to retrieve specific sample  # noqa: E501


    :rtype: str
    """
    try:
        examples = []
        for files in os.listdir(EXAMPLES_DIRECTORY):
            examples.append(files)
        return str(examples), 200
    except:
        return handle_400_error(400)

@REFINER_API.route('/api/cta/<string:cta_name1>/refines/<string:cta_name2>', methods=['GET'])
def refine_ctas(cta_name1,cta_name2):  # noqa: E501
    """Gets refinements between two CTAs.

    By passing in the appropriate options, you can search for ctas which are currently defined in the session  # noqa: E501

    :param cta_name: the name of the CTAs that are to be refined
    :type cta_name: str

    :rtype: Refinement
    """
    try:
        cta1 = get_cta(cta_name1)
        cta2 = get_cta(cta_name2)

        script = ("Cta " + cta_name1 + " = {" + str(cta1["CTA"]) + "}; Cta " + cta_name2 + " = {"
        + str(cta2["CTA"]) + "};" + cta_name1 + " refines? " + cta_name2 + ";")

	scriptResponse = web_script_refinement_checker(str(script),"none","png")
        return jsonify(result=scriptResponse), 200
    except:
        return handle_404_error(404)

@REFINER_API.route('/api/cta', methods=['GET'])
def search_cta(skip=None, limit=None):  # noqa: E501
    """Searches CTAs in your session.

    By passing in the appropriate options, you can search for ctas which are currently defined in the system  # noqa: E501

    :param skip: number of records to skip for pagination
    :type skip: int
    :param limit: maximum number of records to return
    :type limit: int

    :rtype: list
    """

    try:
        return jsonify(session["CTA List"]), 200
    except:
        return handle_404_error(404)

def parse_ctas(script):
    """Parses a script and extracts CTAs from it.

       By passing in a script, it is parsed and CTAs defined are added to the session's list
       of CTAs.

        :param script: Cta refinement script
        :type script: string
    """
    cta_name = ""
    while script.find("Cta") != -1:
        sp_script = script.split()
        index = sp_script.index("Cta")
        cta_name = sp_script[index + 1]
        index = index + 3
        cta_definition = ""

        while not end_of_cta(sp_script[index],sp_script[index + 1]):
            cta_definition = cta_definition + sp_script[index] + " "
            index = index + 1
        cta_obj = {"name" : cta_name, "CTA" : cta_definition + "}"}
        if session.has_key("CTA List"):
            if not cta_present(cta_name):
                append_cta(cta_name,cta_definition)
        else:
            session["CTA List"] = [cta_obj]

        start = script.find("Cta") + 3
        script = script[start:]


def end_of_cta(str,str2):
    """Signifies the end of a CTA object within a script.

       Idenitifies the the tokens that symbolise the end of a CTA definition.

    :param str: String to test for object end tokens
    :type str: string

    :param str2: String to test for object end tokens
    :type str2: string

    :rtype: boolean
    """
    return str.find("};") != -1 or str[-1].find("}") != -1 and str2[0].find(";") != -1

def reformat_script(script):
    """Reformats script for compatibility with 'parse_cta' function.

       By reformatting the script, it can be parsed without errors by 'parse_cta'.

    :param script: CTA refinement script
    :type script: string

    :rtype: string
    """
    sp_script = script.split()
    rf_script = ""
    new_str = ""
    for str in sp_script:
        if str.find(";") != -1:
            for i in str:
                if i == ";":
                    new_str = new_str + " ; "
                else:
                    new_str = new_str + i
            rf_script = rf_script + new_str + " "
            new_str = ""
        else:
            rf_script = rf_script + str + " "
    return rf_script

def cta_present(name):
    """Looks for a specific CTA within the session.

       The name if the target CTA is entered and the function returns
       whether a CTA with a matching name exists.

    :param name: Name of CTA
    :type name: string

    :rtype: boolean
    """
    if not session.has_key("CTA List"):
        return False
    c = -1
    for cta in session["CTA List"]:
        if cta["name"] == name:
            c = c + 1
    return c != -1


def append_cta(name, definition):
    """Adds given CTA to session's CTA List.

       A CTA object is created, and added it to the CTA List
       within the session.

    :param name: Name of CTA
    :type name: string
    :param definition: Definition of the CTA
    :type definition: string

    :rtype: none
    """
    cta_obj = {"name": name, "CTA": definition}
    if session.has_key("CTA List"):
        session["CTA List"].append(cta_obj)
	session.modified = True
    else:
        session["CTA List"] = [cta_obj]

def get_cta(name):
    """Retrieves the given CTA from the session.

       Searches list of CTA's in session and returns a CTA
       if it has a matching name.

    :param name: Name of CTA
    :type name: string

    :rtype: dict
    """
    if session.has_key("CTA List"):
        for cta in session["CTA List"]:
            if cta["name"] == name:
                return cta
    else:
        return None

@REFINER_API.errorhandler(400)
def handle_400_error(_error):
    """Return a http 400 error to client"""
    return make_response(jsonify({'error': 'Invalid Operation'}), 400)


@REFINER_API.errorhandler(404)
def handle_404_error(_error):
    """Return a http 404 error to client"""
    return make_response(jsonify({'error': 'CTA Not found'}), 404)
