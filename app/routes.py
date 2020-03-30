# -*- coding: utf-8 -*-
from flask import Flask, render_template, request, redirect, Response, session, url_for
from app.config import Config as cfg
import requests
import json
import logging
from app import app
from app.main import check_score, create_customer, transform_file_dic, check_input
from app.constant import default_token_dic
from copy import deepcopy
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
    print("test1")
    return render_template("test.html")
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

            with open(cfg.SHOP_TOKEN_FILE, "a") as f:
                shop_toke_dic = deepcopy(default_token_dic)
                shop_toke_dic["shop"]["shop_name"] = request.args.get("shop")
                shop_toke_dic["shop"]["access_token"] = resp_json.get("access_token")
                shop_toke_dic["shop"]["scope"] = resp_json.get("scope")
                shop_token = "{0}\n".format(json.dumps(shop_toke_dic))
                logging.warning("shop_token is {}".format(shop_token))
                f.write(shop_token)
                f.flush()
            return render_template('welcome.html', from_shopify=resp_json,
                                   products="install successful")
        else:
            print("Failed to get access token: %s %s " % resp.status_code, resp.text)
            return render_template('error.html')


@app.route('/qs_for', methods=['GET'])
def qs_for():
    """
    Connect a shopify store
    """
    if request.args.get('shop'):
        shop = request.args.get('shop')
    else:
        return Response(response="Error:parameter shop not found", status=500)

    shop_token_dic = transform_file_dic(cfg.SHOP_TOKEN_FILE)
    if not shop_token_dic or shop not in shop_token_dic:
        return Response(response="Error:this shop not found", status=500)
    qs_url = cfg.SHOPIFY_CONFIG["QS_URI"]
    session['access_token'] = shop_token_dic.get("shop").get("access_token")
    session['scope'] = shop_token_dic.get("shop").get("scope")
    result = redirect(qs_url)
    return result


@app.route('/questionnaire', methods=['GET', 'POST'])
def questionnaire():
    args = dict()
    if request.args.get('shop'):
        shop = request.args.get('shop')
    else:
        return Response(response="Error:parameter shop not found", status=500)
    if request.args.get('email'):
        shop_email_address = request.args.get('email')
    else:
        shop_email_address = "username@domain.com"
    args["shop_email_address"] = shop_email_address
    args["shop"] = shop
    qs_form = QSForm()
    if qs_form.validate_on_submit():
        args["first_name"] = qs_form.first_name.data
        args["last_name"] = qs_form.last_name.data
        args["email"] = qs_form.email.data
        args["order_num"] = qs_form.order_num.data
        args["score"] = qs_form.score.data
        # return "first_name is {0}, and last_name is {1}, and email is {2}, and order_num is {3}, score is {4}, " \
        #        "the session_token is {5}" \
        #     .format(args["first_name"], args["last_name"], args["email"], args["order_num"], args["scope"],
        #             session.get("access_token"))
        result_term = question(args)
        return result_term
    return render_template('questionnaire.html', form=qs_form)


def question(args):
    shop = args["shop"]
    shop_token_dic = transform_file_dic(cfg.SHOP_TOKEN_FILE)
    if not check_input(input_str=args["email"], check_type="email"):
        print("email error")
        return render_template('param_error.html', params="email")
    if not check_input(input_str=args["score"], check_type="score"):
        print("score error")
        return render_template('param_error.html', params="score")
    if not shop_token_dic or shop not in shop_token_dic:
        logging.error("this shop does't exist")
        print("shop error")
        return render_template('param_error.html', param="no shop param")
    access_token = shop_token_dic.get(shop).get("access_token")
    param = dict()
    score = int(args["score"])
    if check_score(score):
        param["first_name"] = args["first_name"]
        param["last_name"] = args["last_name"]
        param["email"] = args["email"]
        param["order_num"] = args["order_num"]
        response = create_customer(access_token, shop, param)
        if response:
            return render_template('submit_success.html', email=args["shop_email_address"])
        else:
            logging.error("create customer has been some error")
            return render_template('error.html')
    else:
        return render_template('contact_us.html')


if __name__ == '__main__':
    flaskrun(app)
