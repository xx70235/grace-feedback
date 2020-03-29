class Config(object):
    SECRET_KEY = "CantStopAddictedToTheShinDigChopTopHeSaysImGonnaWinBig"
    HOST = "www.ycadvisor.com"
    SHOPIFY_CONFIG = {
        'API_KEY': '03e5e92a9189276630e50f24b17f0dc4',
        'API_SECRET': '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',
        'APP_HOME': 'https://' + HOST,
        'CALLBACK_URL': 'https://' + HOST + '/install',
        'REDIRECT_URI': 'https://' + HOST + '/connect',
        'RE_CONNECT_URI': 'https://' + HOST + '/re_connect',
        'QS_URI': 'https://' + HOST + '/questionnaire',
        'SCOPE': 'read_products, read_collection_listings, write_customers'
    }
    SHOP_TOKEN_FILE = "/home/ec2-user/grace-feedback/access_tokens.txt"

