# -*- coding: utf-8 -*-
import requests
from copy import deepcopy

from app.constant import default_customer_dic


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
    default_data = deepcopy(default_customer_dic)
    default_data["customer"]["first_name"] = param_dic["first_name"]
    default_data["customer"]["last_name"] = param_dic["last_name"]
    default_data["customer"]["email"] = param_dic["email"]
    default_data["customer"]["phone"] = param_dic["order_num"]
    endpoint = "/admin/api/2020-01/customers.json"
    #response = requests.get("https://{0}{1}".format(shopname, endpoint), headers=headers)
    response = requests.post("https://{0}{1}".format(shop_name, endpoint), data=default_data, headers=headers)

    if response.status_code == 200:
        return response
    else:
        print("error code is {}".format(response.status_code))
        return False
