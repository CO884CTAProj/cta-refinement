from flask import Flask, render_template, request, url_for, redirect, send_file
import sys
sys.path.append('/var/www/cta_refinement/cta_refinement/dbmModules')
from CtaWebFunctions import *

app = Flask(__name__)

@app.route("/",methods=["POST","GET"])
def home():
    if request.method == "POST":
        scriptInput = request.form["script"]
        response = webScriptRefinementChecker(str(scriptInput))
        return render_template("output.html",script = response)
    else:
        return render_template("index.html")


@app.route("/sample-scripts/atm")
def atm():
    f = open("/var/www/cta_refinement/cta_refinement/dbmModules/Examples/ATM","r")
    src = f.readlines()
    return render_template("ATM.html", src=src, len=len(src))

@app.route("/sample-scripts/fisher-mutual-exclusion")
def fisher():
    f = open("/var/www/cta_refinement/cta_refinement/dbmModules/Examples/FisherMutualExclusion","r")
    src = f.readlines()
    return render_template("fisher.html", src=src, len=len(src))

@app.route("/sample-scripts/ford-credit-portal")
def ford():
    f = open("/var/www/cta_refinement/cta_refinement/dbmModules/Examples/FordCreditWebPortal","r")
    src = f.readlines()
    return render_template("ford.html", src=src, len=len(src))

@app.route("/sample-scripts/ooi-word-counting")
def ooi():
    f = open("/var/www/cta_refinement/cta_refinement/dbmModules/Examples/OOIWordCounting","r")
    src = f.readlines()
    return render_template("ooi.html", src=src, len=len(src))

@app.route("/sample-scripts/scheduled-task-protocol")
def task():
    f = open("/var/www/cta_refinement/cta_refinement/dbmModules/Examples/ScheduledTaskProtocol","r")
    src = f.readlines()
    return render_template("task.html", src=src, len=len(src))

@app.route("/sample-scripts/smtp-client")
def smtp():
    f = open("/var/www/cta_refinement/cta_refinement/dbmModules/Examples/SMTPClient","r")
    src = f.readlines()
    return render_template("smtp.html", src=src, len=len(src))


if __name__ == "__main__":
    app.run(threaded=True)
