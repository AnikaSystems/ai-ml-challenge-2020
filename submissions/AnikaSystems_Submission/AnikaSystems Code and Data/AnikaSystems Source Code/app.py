# app.py - Start GSA EULA parser application web server.
# TODO: Wrap response functions in try/catch... Create single error struct.

# Flask server
import flask
from flask import request
from flask import jsonify
from flask import send_file
from waitress import serve

# Misc
from termcolor import colored
import requests
import os
import datetime
from bson.json_util import dumps
import time

# Local Utils
import mongo
import queue_mon


# Flask configuration
os.environ['OAUTHLIB_INSECURE_TRANSPORT'] = '1' # enable non-HTTPS for testing
APP = flask.Flask(__name__, template_folder='static')
APP.debug = True
APP.secret_key = 'development'
SESSION = requests.Session()


## Response Errors #############################################################

def response_error(vroute, vmesg):
    # Return a struct used by all routes that indicates an error occured.
    
    print("[* app] Request error: %s [%s]" % (vroute, vmesg))
    return jsonify({
        "error": str(vmesg)
    })


## Page Routes #################################################################

@APP.route('/')
def homepage():
    """Render homepage."""

    return flask.render_template('index.html')


@APP.route('/process_eula', methods=['POST'])
def process_eula():
    """Add EULA file to queue to be OCR extracted and classified."""

    try:
        # Get file from request.
        vfile = request.files.get('file')
        print("[* app] Process file: [%s]" % vfile.filename)

        # Queue structure:
        vbytes = vfile.read()
        vqueue_item = {
            "fname": vfile.filename,
            "upload_time": str(datetime.datetime.now()),
            "completed": 0,
            "fsize": len(vbytes),
            "bytes": vbytes,
        }

        # Add to mongo queue db for processing.
        vres = mongo.queue_add(vqueue_item)

        return jsonify(dumps(vres))

    except Exception as e:
        response_error("%s %s" % (request.method, request.path), e)


@APP.route('/queue_files', methods=['GET'])
def queue_files():
    """Return array of all files in the queue."""
    
    try:
        return jsonify(dumps(mongo.queue_get()))
    except Exception as e:
        response_error("%s %s" % (request.method, request.path), e)


@APP.route('/eulas_db', methods=['GET'])
def eulas_db():
    """Return array of all files in the EULAs DB."""
    
    print("[* app] Rerieving docs!")
    vstime = time.time()
  
    try:
        docs = mongo.docs_get()
        print("[* app] Mongo docs recieved. Download time: [%s]" % str(time.time()-vstime))
        print("[* app] List size: [%s] KB\n" % (len(str(docs))/1024))
        return jsonify(dumps(docs))
    except Exception as e:
        response_error("%s %s" % (request.method, request.path), e)


@APP.route('/eula', methods=['GET'])
def get_eula():
    """Return a EULA document by querying its ID."""

    print("[* app] Rerieving EULA by ID")
    vstime = time.time()
    
    try:
        veula_id = request.args.get('id')
        vdoc = mongo.get_doc(veula_id)
        
        print("[* app] EULA retrieved. Download time: [%s]" % str(time.time()-vstime))
        print("[* app] DOC size: [%s] KB\n" % (len(str(vdoc))/1024))

        return jsonify(dumps(vdoc))
    except Exception as e:
        response_error("%s %s" % (request.method, request.path), e)


@APP.route('/eula_bin', methods=['GET'])
def get_eula_binary():
    """Return a EULA document, and its binary data, by querying its ID."""

    print("[* app] Rerieving EULA by ID")
    vstime = time.time()
    
    try:
        veula_id = request.args.get('id')
        vdoc = mongo.get_doc_binary(veula_id)
        
        print("[* app] EULA retrieved. Download time: [%s]" % str(time.time()-vstime))
        print("[* app] DOC size: [%s] KB\n" % (len(str(vdoc))/1024))

        return jsonify(dumps(vdoc))
    except Exception as e:
        response_error("%s %s" % (request.method, request.path), e)


## Run Server ##################################################################

if __name__ == '__main__':
    import sys

    try:
        queue_mon.run()
        print("[* app] Server is running")
        serve(APP, host="0.0.0.0", port=5000)
    except KeyboardInterrupt:
        print("[* app] Exit application server.")
        sys.exit()