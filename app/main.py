# -*- coding: utf-8 -*-
import requests
from copy import deepcopy
import logging
import json
import os
import re
import smtplib
from email.mime.text import MIMEText
from email.header import Header

from app.config import Config as cfg


from app.constant import default_customer_dic

email_pattern = r'^[\d\w\.]+@[\d\w]+\.com$'
score_pattern = r'^[1-5]$'


def check_input(input_str, check_type="email"):
    if check_type == "email":
        return re.match(email_pattern, input_str)
    if check_type == "score":
        return re.match(score_pattern, input_str)


def check_score(score=1):
    """
    :param score: 用户的评分
    :return: False or True  4-5分返回true, 1-3 分返回 false
    """

    if not isinstance(score, int) or score < 1 or score > 5:
        return False
        #raise Exception("the score param is not right, and it should be 1 - 5")
    elif 1 <= score <= 3:
        return False
    elif 4 <= score <= 5:
        return True


def create_customer(access_token, shop_name, param_dic):
    """ Great a new customer """
    headers = {
        "X-Shopify-Access-Token": access_token,
        "Content-Type": "application/json"
    }
    print("shopname: " + shop_name)
    default_data = deepcopy(default_customer_dic)
    default_data["customer"]["first_name"] = param_dic["first_name"]
    default_data["customer"]["last_name"] = param_dic["last_name"]
    default_data["customer"]["email"] = param_dic["email"]
    default_data["customer"]["tags"] = "order_num: " + param_dic["order_num"]
    endpoint = "/admin/api/2020-01/customers.json"
    #response = requests.get("https://{0}{1}".format(shopname, endpoint), headers=headers)
    response = requests.post("https://{0}{1}".format(shop_name, endpoint), data=json.dumps(default_data), headers=headers)

    if response.status_code == 201:
        logging.warning(response.content)
        return response
    elif response.status_code == 422:
        try:
            logging.error("error message type {}".format(str(response.content)))
            json_str = response.content.decode()
            print(json_str)
            content_dic = json.loads(json_str)
            if "email" in content_dic["errors"] and content_dic["errors"]["email"][0] == "has already been taken":
                return "DP_EMAIL"
            else:
                return "OTHER_ERRORS"
        except Exception as e:
            logging.error(e, exc_info=True)
            return "OTHER_ERRORS"
    else:
        logging.error("url is https://{0}{1}".format(shop_name, endpoint))
        logging.error("error code is {}".format(response.status_code))
        logging.error("error message is {}".format(response.content))
        return "OTHER_ERRORS"


def transform_file_dic(file_path):
    try:
        result_dic = dict()
        if os.path.isfile(file_path):
            with open(file_path, "r") as f:
                file_lines = f.readlines()
                for line in file_lines:
                    if line is not "":
                        pair_dic = json.loads(line)
                        shop_name = pair_dic["shop"]["shop_name"]
                        access_token = pair_dic["shop"]["access_token"]
                        scope = pair_dic["shop"]["scope"]
                        result_dic[shop_name] = {"access_token": access_token, "scope": scope}
        return result_dic
    except Exception as e:
        logging.error("transform_file_dic method has error, error message is {}".format(e), exc_info=True)
        return None


def send_email(shop, email_to):
    msg_to_list = list()
    msg_to_list.append(email_to)
    shop_address = "https://" + shop
    email_from = cfg.EMAIL_FROM
    email_auth = cfg.EMAIL_AUTH
    if not check_input(email_to, check_type="email"):
        return "NOT_RIGHT_EMAIL"
    email_subject = "{}: your account has been registered !".format(shop)
    email_content = "Hi there,\n  As a new customer of Shopify shop {0}, we prepare a lot of new products for you," \
                    " you can access it through address {1}. " \
                    "This is an automatically send email, please do not reply.\n \n  ----com from {2}"\
        .format(shop, shop_address, shop)
    email_msg = MIMEText(email_content)
    email_msg['Subject'] = Header(email_subject)
    email_msg['From'] = email_from
    email_msg['To'] = ",".join(msg_to_list)
    try:
        s = smtplib.SMTP_SSL("smtp.163.com", 465)
        # 登录到邮箱
        s.login(email_from, email_auth)
        # 发送邮件：发送方，收件方，要发送的消息
        s.sendmail(email_from, msg_to_list, email_msg.as_string())
        print("send email successful")
    except Exception as e:
        logging.error("send email failed, the error message is {}".format(e), exc_info=True)


if __name__ == "__main__":
    result = check_input(input_str="12", check_type="score")
    if result:
        print("yes")
    else:
        print("no")

    result1 = check_input(input_str="sdfhas@112", check_type="email")

    if result1:
        print("yes1")
    else:
        print("no1")

    send_email("http-tankers.myshopify.com", "asqhaqs@163.com")

