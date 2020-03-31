# -*- coding: utf-8 -*-
import requests
from copy import deepcopy
import logging
import json
import os
import re

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

