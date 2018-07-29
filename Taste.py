# [START app]
import os
from flask import Flask, jsonify, request, Blueprint

from API.Taste.taste_test import TasteTest

app = Flask(__name__)
app.register_blueprint(TasteTest)


@app.route('/')
def hello():
    """Return a friendly HTTP greeting."""
    return 'Hello World!'

@app.route('/version/')
def version():
    version = {}
    with open("version.py") as fp:
        exec(fp.read(), version)
    return jsonify({"version":str(version['__version__'])})

@app.route('/git/')
def git_status():
    gitDict = {"Branch":"", "Commit":{"Commit hash":"", "Abbreviated commit hash":"", "Tree hash":"", "Abbreviated tree hash":"", "Parent hashes":"", "Abbreviated parent hashes":"", "Author name":"", "Author email":"", "Author date":"", "Author date, relative":"", "Committer name":"", "Committer email":"", "Committer date":"", "Committer date, relative":"", "Subject":""}}

    try:
        branch = os.popen("git rev-parse --abbrev-ref HEAD").read()
        gitDict["Branch"] = branch.rstrip("\n")
    except:
        print("Something went wrong with the command.")

    try:
        log = os.popen("git log --pretty=format:\"%H,%h,%T,%t,%P,%p,%an,%ae,%ad,%ar,%cn,%ce,%cd,%cr,%s\" -1").read()
        logList = log.split(",")

        gitDict["Commit"]["Commit hash"] = logList[0]
        gitDict["Commit"]["Abbreviated commit hash"] = logList[1]
        gitDict["Commit"]["Tree hash"] = logList[2]
        gitDict["Commit"]["Abbreviated tree hash"] = logList[3]
        gitDict["Commit"]["Parent hashes"] = logList[4]
        gitDict["Commit"]["Abbreviated parent hashes"] = logList[5]
        gitDict["Commit"]["Author name"] = log.split(",")[6]
        gitDict["Commit"]["Author email"] = log.split(",")[7]
        gitDict["Commit"]["Author date"] = log.split(",")[8]
        gitDict["Commit"]["Author date, relative"] = log.split(",")[9]
        gitDict["Commit"]["Committer name"] = log.split(",")[10]
        gitDict["Commit"]["Committer email"] = log.split(",")[11]
        gitDict["Commit"]["Committer date"] = log.split(",")[12]
        gitDict["Commit"]["Committer date, relative"] = log.split(",")[13]
        gitDict["Commit"]["Subject"] = log.split(",")[14].split("\n")[0]
    except:
        print("Something went wrong with the command.")

    return jsonify(gitDict)


if __name__ == '__main__':
    app.run(host='127.0.0.1')
# [END app]
