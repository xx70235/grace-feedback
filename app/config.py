class Config(object):
    SECRET_KEY = "CantStopAddictedToTheShinDigChopTopHeSaysImGonnaWinBig"
    HOST = "www.ycadvisor.com"
    SHOPIFY_CONFIG = {
        #'API_KEY': '5621465025cca3faec8def69d539539e',
        'API_KEY': '03e5e92a9189276630e50f24b17f0dc4',
        #'API_SECRET': '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',
        'API_SECRET': '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',
        'APP_HOME': 'https://' + HOST,
        'CALLBACK_URL': 'https://' + HOST + '/install',
        'REDIRECT_URI': 'https://' + HOST + '/connect',
        'SCOPE': 'read_products, read_collection_listings, write_customers'
    }

    default_customer_dic = {
        "customer": {
            "first_name": "Steve",
            "last_name": "Lastnameson",
            "email": "steve.lastnameson@example.com",
            "phone": "+15142546011",
            "verified_email": True,
            "addresses": [
                {
                    "address1": "123 Oak St",
                    "city": "Ottawa",
                    "province": "ON",
                    "phone": "555-1212",
                    "zip": "123 ABC",
                    "last_name": "Lastnameson",
                    "first_name": "Mother",
                    "country": "CA"
                }
            ]
        }
    }