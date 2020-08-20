# mongo.py - Wrapper functions for connecting to mongo database.
# Store credentials in environment variables.

from pymongo import MongoClient
from bson.objectid import ObjectId
from datetime import datetime
import urllib
import os
import time

# Store credentials in environment variables.
VMONGO_CONN_STRING = os.getenv('MONGO_CONNSTRING')
VDB_NAME = None

# Create mongo client.
vclient = MongoClient(VMONGO_CONN_STRING)

# Get collection references.
vdb = vclient["gsa_challenge"]
vcol = vdb.main
vcol_queue = vdb.queue


## CRUD basic ##################################################################

def insert_doc(vdoc):
    # Insert document into main forms database collection.
    
    try:
        print("[* mongo] Inserting document into main collection")
        vdoc["timestamp"] = datetime.now()
        vid = vcol.insert_one(vdoc)
        print("[* mongo] Doc inserted succesfully: [%s]" % str(vid.inserted_id))

    except Exception as e:
        print("[* mongo] Could not insert doc: %s" % e)
        return { "error": str(e) }

    vdoc["_id"] = vid.inserted_id
    return vdoc


def docs_get():
    """Get the last documents in the collection."""
    vdocs = list(vcol.find(None, {"bytes": 0,  "eula_text":0, "clauses":0}))
    # print(len(vdocs))
    return vdocs


def queue_get(get_bytes=False):
    # Return entire queue structure.
    try:
        # print("[* mongo] Retrieve queue data...")

        if get_bytes:
            vqueue = list(vcol_queue.find())
        else:
            vqueue = list(vcol_queue.find({}, {"bytes": 0}))
        return vqueue
    except Exception as e:
        print("[* mongo] Could not retrieve queue: %s" % e)
        return []


def get_doc(vdoc_id):
    # Retrieve a document from mongoDB by ID.
    try:
        print("[* mongo] Get doc: %s" % vdoc_id)
        vdoc = vcol.find_one({'_id': ObjectId(vdoc_id)}, {"bytes":0})
        print("[* mongo] Doc %s retrieved successfuly!" % vdoc_id)
        return vdoc
    except Exception as e:
        print("[* mongo] Could not get doc %s. %s" % (vdoc_id, e))
        return { "error": e }


def get_doc_binary(vdoc_id):
    # Retrieve a document from mongoDB by ID, including its bytes DATA.
    try:
        print("[* mongo] Get doc: %s" % vdoc_id)
        vdoc = vcol.find_one({'_id': ObjectId(vdoc_id)}, {"eula_text":0, "clauses":0})
        print("[* mongo] Doc %s retrieved successfuly!" % vdoc_id)
        return vdoc
    except Exception as e:
        print("[* mongo] Could not get doc %s. %s" % (vdoc_id, e))
        return { "error": e }


## Queue Functions #############################################################

def queue_add(vdoc):
    # Add a document to extraction queue.
    # It used to show on front end.
    # TODO: Should accept a form path...
    try:
        print("[* mongo] Add to queue: %s" % vdoc["fname"])
        vres = vcol_queue.insert(vdoc)
        return { "_id": str(vres) }
    except Exception as e:
        print("[* mongo] Could not add to queue: %s. %s." % (vdoc["fname"], e))
        return { "error": e }


def queue_remove(vdoc_id):
    # Delete queue item by ID.
    try:
        print("[* mongo] Remove from queue: %s" % vdoc_id)
        vcol_queue.delete_one({
            "_id": ObjectId(vdoc_id)
        })
    except Exception as e:
        print("[* mongo] Could not remove from queue: %s. %s." % (vdoc_id, e))
        return { "error": e }
    
    return None


def queue_progress(vqueue_id, vdone=False):
    # Update the progress of a queue item periodically

    if vdone:
        print("[* mongo] Run queue updater (completed) [%s]" % vqueue_id)
        try:
            vcol_queue.update_one({"_id": ObjectId(vqueue_id)}, 
                {"$set": {"completed": 100}})
        except Exception as e:
            print("[* mongo] Could not update queue: %s. %s." % (vqueue_id, e))
            return
    else:
        print("[* mongo] Run queue updater on [%s]" % vqueue_id)
        vprog = 0
        while vprog <= 95:
            try:
                vcol_queue.update_one({"_id": ObjectId(vqueue_id)}, 
                    {"$set": {"completed": vprog}})
                vprog += 5
                time.sleep(3.5)
            except Exception as e:
                print("[* mongo] Could not update queue: %s. %s." % (vqueue_id, e))
                return