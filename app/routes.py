# -*- coding: utf-8 -*-
from flask import Flask, render_template, request, redirect, Response, session, url_for
from app.config import Config as cfg
import requests
import json
import logging
from app import app
from app.main import check_score, create_customer
from app.flaskrun import flaskrun
from app.form_tem import QSForm


# app = Flask(__name__, template_folder="templates")
# # app.debug = True
# app.secret_key = cfg.SECRET_KEY


@app.route("/")
def index():
    return "The URL for this page is {}".format(url_for("index"))


@app.route('/products', methods=['GET'])
def products():
    """ Get a stores products """
    headers = {
        "X-Shopify-Access-Token": session.get("access_token"),
        "Content-Type": "application/json"
    }
    
    logging.warning("shop: "+session.get("shop"))
    logging.warning("access_token: " + session.get("access_token"))

    endpoint = "/admin/api/2020-01/products.json"
    response = requests.get("https://{0}{1}".format(session.get("shop"),
                                                   endpoint), headers=headers)

    if response.status_code == 200:
        return response
    else:
        return False


def get_registered_webhooks_for_shop():
    headers = {
        "X-Shopify-Access-Token": session.get("access_token"),
        "Content-Type": "application/json"
    }

    get_webhooks_response = requests.get("https://" + session.get("shop") +
                                         "/admin/webhooks.json",
                                         headers=headers)

    if get_webhooks_response.status_code == 200:
        webhooks = json.loads(get_webhooks_response.text)
        print(webhooks)
        return webhooks
    else:
        return False


@app.route('/webhooks', methods=['GET', 'POST'])
def webhooks():
    if request.method == "GET":
        return render_template('webhooks.html',
                               webhooks=get_registered_webhooks_for_shop())
    else:
        webhook_data = json.loads(request.data)
        print("Title: {0}".format(webhook_data.get("title")))
        return Response(status=200)


@app.route('/register_webhook', methods=['GET'])
def register_webhook():
    headers = {
        "X-Shopify-Access-Token": session.get("access_token"),
        "Content-Type": "application/json"
    }

    payload = {
        "webhook": {
            "topic": "products/update",
            "address": "https://{0}/webhooks".format(cfg.HOST),
            "format": "json"
        }
    }
    response = requests.post("https://" + session.get("shop")
                             + "/admin/webhooks.json",
                             data=json.dumps(payload), headers=headers)

    if response.status_code == 201:

        return render_template('register_webhook.html',
                               webhook_response=json.loads(response.text))
    else:
        return Response(response="{0} - {1}".format(response.status_code,
                                                    response.text), status=200)


@app.route('/install', methods=['GET'])
def install():
    """
    Connect a shopify store
    """
    if request.args.get('shop'):
        shop = request.args.get('shop')
    else:
        return Response(response="Error:parameter shop not found", status=500)

    auth_url = "https://{0}/admin/oauth/authorize?client_id={1}&scope={2}&redirect_uri={3}".format(
        shop, cfg.SHOPIFY_CONFIG["API_KEY"], cfg.SHOPIFY_CONFIG["SCOPE"],
        cfg.SHOPIFY_CONFIG["REDIRECT_URI"]
    )
    print("Debug - auth URL: ", auth_url)
    return redirect(auth_url)


@app.route('/test1', methods=['GET'])
def generate_token():
    print(session["shop"])
    return Response(response="test path", status=200)
    # if request.args.get('shop'):
    #     shop = request.args.get('shop')
    # else:
    #     return Response(response="Error:parameter shop not found", status=500)

    # auth_url = "https://{0}/admin/oauth/authorize?client_id={1}&scope={2}&redirect_uri={3}".format(
    #     shop, cfg.SHOPIFY_CONFIG["API_KEY"], cfg.SHOPIFY_CONFIG["SCOPE"],
    #     cfg.SHOPIFY_CONFIG["REDIRECT_URI"]
    # )
    # print("Debug - auth URL: ", auth_url)
    # return redirect(auth_url)


@app.route('/connect', methods=['GET'])
def connect():
    if request.args.get("shop"):
        params = {
            "client_id": cfg.SHOPIFY_CONFIG["API_KEY"],
            "client_secret": cfg.SHOPIFY_CONFIG["API_SECRET"],
            "code": request.args.get("code")
        }
        resp = requests.post(
            "https://{0}/admin/oauth/access_token".format(
                request.args.get("shop")
            ),
            data=params
        )

        if 200 == resp.status_code:
            resp_json = json.loads(resp.text)

            session['access_token'] = resp_json.get("access_token")
            session['shop'] = request.args.get("shop")
            logging.warning("contect access_token:" + session['access_token'])
            logging.warning("contect shop:" + session['shop'])
            response = products()
            return render_template('welcome.html', from_shopify=resp_json,
                                   products=response.json())
        else:
            print("Failed to get access token: %s %s " % resp.status_code, resp.text)
            return render_template('error.html')


@app.route('/questionnaire', methods=['GET', 'POST'])
def questionnaire():
    qs_form = QSForm()
    if qs_form.validate_on_submit():
        args = dict()
        args["first_name"] = qs_form.first_name.data
        args["last_name"] = qs_form.last_name.data
        args["email"] = qs_form.last_name.data
        args["order_num"] = qs_form.order_num.data
        args["scope"] = qs_form.score.data
        return "first_name is {0}, and last_name is {1}, and email is {2}, and order_num is {3}, score is {4}, " \
               "the session_token is {5}" \
            .format(args["first_name"], args["last_name"], args["email"], args["order_num"], args["scope"],
                    session.get("access_token"))
    return render_template('questionnaire.html', form=qs_form)


def question(args):
    if not args.has_key("first_name") or not args.has_key("last_name") \
            or not args.has_key("email") or not args.has_key("scope") or not args.has_key("order_num"):
        return render_template('error.html')
    param = dict()
    score = int(args["score"])
    if check_score(score):
        return "first_name is {0}, and last_name is {1}, and email is {2}, and order_num is {3}, score is {4}, " \
               "the session_token is {5}"\
            .format(args["first_name"], args["last_name"], args["email"], args["order_num"], args["scope"], session.get("access_token"))
        # param["first_name"] = args["first_name"]
        # param["last_name"] = args["last_name"]
        # param["email"] = args["email"]
        # param["order_num"] = args["order_num"]
        # access_token = session.get("access_token")
        # shop_name = session.get("shop")
        # response = create_customer(access_token, shop_name, param)
        # print(response)
    else:
        # todo 创建一个提示评价不足的页面
        return render_template('error.html')


if __name__ == '__main__':
    flaskrun(app)
