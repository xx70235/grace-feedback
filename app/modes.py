# -*- coding: utf-8 -*-


class User(object):

    __tablename__ = "user"

    def __init__(self, shop_id, shop_name, passwd, scope, access_token, shop_email, contact_url):
        self.shop_id = shop_id
        self.shop_name = shop_name
        self.passwd = passwd
        self.scope = scope
        self.access_token = access_token
        self.shop_email = shop_email
        self.contact_url = contact_url



