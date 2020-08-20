# queue_mon.py - Monitor queue structure in mongo DB until a document is ready to be processed by model.
#                Runs in a seperate thread from main process.


import threading
import time
from termcolor import colored
import os
import uuid

# Local Utils
import mongo
import classifier
import datetime
import docx_parse
import pdf_to_string


# Increment each cycle of monitor check. Used for debugging.
vinc = 0


def queue_mon():
    # Retrieve queue documents, and process each one. Infinite loop.

    global vinc
    print("%s Run queue monitor" % (colored("[* queue_mon]", "blue")))

    while True:
        print("\n%s Checking queue...[%s]" % (colored("[* queue_mon]", "blue"), vinc))
        vinc += 1

        # Retrieve all documents in queue.
        vqueue = mongo.queue_get(get_bytes=True)
        print(colored("[* queue_mon]", "blue") + " Docs found: [%s]" % len(vqueue))

        if len(vqueue) > 0:
            for vitem in vqueue:
                # Process queue item
                """ Queue Item Sample: {
                    "_id",
                    "fname",
                    "eula_text",
                    "clauses",
                    "upload_time",
                    "completed",
                    "bytes",
                }"""

                # Create predictions
                verror = False
                try:
                    # Run multithread queue progress updater
                    print("[* mongo] Processing queue item: [%s]" % vitem['_id'])
                    vprog_thread = threading.Thread(target=mongo.queue_progress, args=(vitem['_id'], ))
                    vprog_thread.start()
                    
                    # Parse and classify document
                    vpreds = run_classifier(vitem)

                    # Stop progress updater
                    vprog_thread.join()
                    mongo.queue_progress(vitem['_id'], vdone=True)

                except Exception as e:
                    verror = str(e)

                # Check for errors
                if not verror is False:
                    print("[* queue_mon] An error occured during classification: [%s]" % verror)

                else:
                    # Add into main database
                    vdb_item = {
                        "fname": vitem["fname"],
                        "eula_text": vpreds["text"],
                        "clauses": vpreds["clauses"], # Contains model predictions.
                        "bytes": vitem["bytes"], # PDF file data
                        "upload_time": str(datetime.datetime.now()),

                        # Add these fields to avoid having to send large structures to front end.
                        "num_clauses": len(vpreds["clauses"]),
                        "num_unacceptable": num_unacceptable(vpreds["clauses"]),
                        "avg_confidence": avg_accuracy(vpreds["clauses"])
                    }
                    mongo.insert_doc(vdb_item)

                # Remove from queue
                mongo.queue_remove(vitem["_id"])

        time.sleep(5)


def avg_accuracy(vclauses):
    # Average conf score
    res = 0
    for vc in vclauses:
        res += vc["confidence"]
    return round(res / len(vclauses), 2)


def num_unacceptable(vclauses):
    # Count number clauses that are unacceptable.
    res = 0
    for vc in vclauses:
        if not vc["acceptable"]: res+=1
    return res


def run_classifier(vitem):
    # Parse the document in the queue and classify its clauses.

    # Get extension
    vext = vitem["fname"].split('.')[-1].upper()

    # Create temp file.
    vtmp_path = "tmp_%s.%s" % (str(uuid.uuid4()), vext)
    vbytes = None
    with open(vtmp_path, 'wb+') as vfp:
        vbytes = vitem["bytes"]
        vfp.write(vbytes)
        vfp.close()

    print("[* queue_mon] File extension: [%s]" % vext)

    # Convert DOCX to PDF
    if vext == "DOC" or vext == "DOCX":
        print("[* queue_mon] Parse DOCX into PDF!")
        vtmp_pdf = docx_parse.docx_to_pdf(vtmp_path)
        # Replace document bytes here with PDF ones? For preview...
        os.remove(vtmp_path)
    else:
        vtmp_pdf = vtmp_path

    # Parse file into clauses.
    vparsed = pdf_to_string.pdf_to_string(vtmp_pdf)

    # Delete file
    try:
        print("[* queue_mon] Deleting tmp file: [%s]" % vtmp_path)
        os.remove(vtmp_path)
    except: pass
    
    # Run classifier
    vpreds = classifier.classify_clauses(vparsed["clauses"])

    return {
        "clauses": vpreds,
        "text": vparsed["text"]
    }


def run():
    # Run queue as a seperate thread, in order to not block main server thread.
    try:
        print("%s Start queue mon thread..." % (colored("[* queue_mon]", "blue")))
        vthread = threading.Thread(target=queue_mon)
        vthread.daemon=True
        vthread.start()  
    except (KeyboardInterrupt, SystemExit) as e:
        return
        sys.exit()


if __name__ == "__main__":
    # DEBUG
    import sys
    try:
        print("[* queue_mon] Running queue monitor in DEBUG mode.")
        queue_mon()
    except KeyboardInterrupt:
        sys.exit()