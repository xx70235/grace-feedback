class Config(object):
    SECRET_KEY = "CantStopAddictedToTheShinDigChopTopHeSaysImGonnaWinBig"
    HOST = "www.ycadvisor.com/apps/grace-feedback"

    SHOPIFY_CONFIG = {
        'API_KEY': '5621465025cca3faec8def69d539539e',
        'API_SECRET': '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',
        'APP_HOME': 'https://' + HOST,
        'CALLBACK_URL': 'http://' + HOST + '/install',
        'REDIRECT_URI': 'http://' + HOST + '/connect',
        'SCOPE': 'read_products, read_collection_listings'
    }