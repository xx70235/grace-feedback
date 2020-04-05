# -*- coding: utf-8 -*-
from flask import Flask, render_template, request, redirect, Response, session, url_for
from app.config import Config as cfg
import requests
import json
import logging

from app import app
from app.main import check_score, create_customer,  check_input, get_md5, check_config_input
from app.modes import User
from app.dao import save_user_with_check, query_user_with_close_by_id
from app.constant import default_token_dic
from app.flaskrun import flaskrun
from app.form_tem import QSForm, ConfigForm
from app.main import send_email

logging.basicConfig(format='%(asctime)s %(filename)s[line:%(lineno)d] %(levelname)s: %(message)s', level=logging.WARNING)
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
            shop_name = request.args.get("shop")
            shop_id = get_md5(shop_name + cfg.SALT_VALUE)
            scope = resp_json.get("scope")
            access_token = resp_json.get("access_token")
            shop_email = default_token_dic["shop"]["shop_email"]
            contact_url = "https://" + shop_name + "/pages/contact-us"
            passwd = shop_id
            user = User(shop_id=shop_id, shop_name=shop_name, passwd=passwd, scope=scope, access_token=access_token,
                        shop_email=shop_email, contact_url=contact_url)
            save_user_with_check(user)
            session["account"] = shop_name
            session["password"] = passwd
            return render_template('install_successful.html', account=shop_name, passwd=passwd)
        else:
            logging.error("Failed to get access token: %s %s " % resp.status_code, resp.text)
            return render_template('error.html')


@app.route('/login_or_redirect', methods=['GET', 'POST'])
def login_or_redirect():
    account = session.get("account")
    password = session.get("password")
    if account and password:
        shop_id = get_md5(account + cfg.SALT_VALUE)
        user_l = query_user_with_close_by_id(shop_id)
        if not user_l or user_l.passwd != password:
            return render_template("login.html")
        logging.warning("login_or_redirect password is {}".format(password))
        return render_template("set_config.html", account=account, password_old=password)
    return render_template("login.html", message="init")


@app.route('/login', methods=['POST'])
def login():
    if request.method != 'POST':
        return render_template("method_error.html", error_type="not_post_method")
    post_data = request.get_data()
    logging.warning("login info: post data is {}".format(post_data))
    try:
        json_data = json.loads(post_data.decode("utf-8"))
    except Exception:
        json_data = {"account": "", "password": ""}
    account_name = json_data.get("account")
    password = json_data.get("password")
    if account_name and password:
        shop_id = get_md5(account_name + cfg.SALT_VALUE)
        user_l = query_user_with_close_by_id(shop_id)
        if not user_l or user_l.passwd != password:
            logging.warning("account or password error")
            return render_template("login.html", sign="error")
        return render_template("set_config.html", account=account_name, password_old=password)
    else:
        return render_template("login.html", sign="error")


@app.route('/set_config', methods=['POST'])
def set_config():
    if request.method != 'POST':
        return render_template("method_error.html", error_type="not_post_method")
    post_data = request.get_data()
    logging.warning("set config info: post data is {}".format(post_data))

    try:
        json_data = json.loads(post_data.decode("utf-8"))
    except Exception:
        json_data = {"account": "", "email": "", "contact_url": "", "password_new": "", "password_old": ""}

    args = dict()
    args["account"] = json_data.get("account").strip()
    args["email"] = json_data.get("email").strip()
    args["contact_url"] = json_data.get("contact_url").strip()
    args["password_old"] = json_data.get("password_old").strip()
    args["password_new"] = json_data.get("password_new").strip()

    check_result = check_config_input(email=args["email"], password=args["password_new"], contact_us=args["contact_url"])
    if check_result == "no_email":
        return render_template("set_config.html", sign="no_email")
    if check_result == "no_url":
        return render_template("set_config.html", sign="no_url")
    if check_result == "error":
        return render_template("set_config.html", sign="error")
    result_term = save_config(args)
    if result_term == "OK":
        return render_template("update_config.html", message="update successful")
    elif result_term == "NO_USER":
        return render_template("update_config.html", message="update error, no this user")
    elif result_term == "WRONG_PASS":
        return render_template("update_config.html", message="update error, password is not right")
    return render_template("update_config.html", message="update error, there is something wrong")


def save_config(args):
    shop_id = get_md5(args.get("account") + cfg.SALT_VALUE)
    user_info = query_user_with_close_by_id(shop_id)
    if not user_info:
        return "NO_USER"
    else:
        if user_info.passwd != args.get("password_old"):
            return "WRONG_PASS"
        if args.get("password_new") != "":
            user_info.passwd = args.get("password_new")
        if args.get("email") != "":
            user_info.shop_email = args.get("email")
        if args.get("contact_url") != "":
            user_info.contact_url = args.get("contact_url")
        save_user_with_check(user_info)
        return "OK"





@app.route('/thanks', methods=['GET', 'POST'])
def thanks():

    return render_template("end_access.html")


@app.route('/submit_success', methods=['GET', 'POST'])
def submit_success():
    if request.args.get('shop_email'):
        shop_email = request.args.get('shop_email')
    else:
        return Response(response="Error:parameter shop_email not found", status=500)
    return render_template("submit_success.html", email=shop_email)


@app.route('/questionnaire', methods=['GET', 'POST'])
def questionnaire():
    args = dict()
    if request.args.get('shop'):
        shop = request.args.get('shop')
    else:
        return Response(response="Error:parameter shop not found", status=500)
    args["shop"] = shop
    qs_form = QSForm(score="1")  # 评分为隐藏框，根据用户打的星号来赋值，默认为1
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
    comment_on_amazon = "https://www.ycadvisor.com/submit_success"
    end_access = "https://www.ycadvisor.com/thanks"
    shop_id = get_md5(shop + cfg.SALT_VALUE)
    user_info = query_user_with_close_by_id(shop_id)

    if not check_input(input_str=args["email"], check_type="email"):
        print("email error")
        return render_template('param_error.html', params="email")
    if not check_input(input_str=args["score"], check_type="score"):
        print("score error")
        return render_template('param_error.html', params="score")
    if not user_info:
        logging.error("this shop does't exist")
        print("shop error")
        return render_template('param_error.html', param="no shop param")
    access_token = user_info.access_token
    param = dict()
    score = int(args["score"])
    if check_score(score):
        param["first_name"] = args["first_name"]
        param["last_name"] = args["last_name"]
        param["email"] = args["email"]
        param["order_num"] = args["order_num"]
        response = create_customer(access_token, shop, param)
        if response == "OTHER_ERRORS":
            logging.error("create customer has been some error")
            return render_template('error.html')
        elif response == "DP_EMAIL":
            # 已注册用户，直接下一步
            return render_template('qs_for_comment.html', email=user_info.shop_email, submit=comment_on_amazon,
                                   end_access=end_access)
        else:
            send_email(shop=shop, email_to=param["email"])       # 成功创建用户，发送给其注册成功的邮件
            return render_template('qs_for_comment.html', email=user_info.shop_email, submit=comment_on_amazon,
                                   end_access=end_access)
    else:
        param["first_name"] = args["first_name"]
        param["last_name"] = args["last_name"]
        param["email"] = args["email"]
        param["order_num"] = args["order_num"]
        response = create_customer(access_token, shop, param)
        if response == "OTHER_ERRORS":
            logging.error("create customer has been some error")
            return render_template('error.html')
        elif response == "DP_EMAIL":
            logging.warning("old costumer")
            return render_template('contact_us_old_user.html', email=user_info.shop_email,
                                   contact_us=user_info.contact_url, end_access=end_access)
        send_email(shop=shop, email_to=param["email"])
        return render_template('contact_us.html', contact_us=user_info.contact_url, end_access=end_access)


if __name__ == '__main__':
    flaskrun(app)
