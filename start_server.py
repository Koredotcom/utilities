""" FaqServer serves knowledge graph content"""

import os
import imp
import logging
import traceback
from flask import Flask
from pdf_extraction.code_util.config.ConfigManager import ConfigManager
from logging.handlers import TimedRotatingFileHandler
from tornado.wsgi import WSGIContainer
from tornado.httpserver import HTTPServer
from tornado.ioloop import IOLoop


def init_routes(app):
    """this methd loads all the routes defined in routes folder."""
    files = os.listdir("./share/routes")
    for item in files:
        if item[0] != '.':
            name, ext = item.split('.')
            if ext == "py":
                route = imp.load_source(name, './share/routes/' + item)
                route.init(app)

if __name__ == "__main__":
    config_manager = ConfigManager()
    log_conf = config_manager.load_config(key='log')
    handler = TimedRotatingFileHandler(filename=log_conf.get("DEBUG_LOG"), when='midnight', backupCount=365)
    logging.basicConfig(
        format=log_conf.get("FORMAT_STRING"),
        filename=log_conf.get("DEBUG_LOG"),
        level=logging.ERROR,
        handlers=[handler])

    logger = logging.getLogger(__name__)

    app = Flask(__name__)
    init_routes(app)

    server_conf = config_manager.load_config(key='server')
    ssl_conf = config_manager.load_config(key='ssl')
    logger.info("Logging is set up.")
    print "=="*15,"PDF extarction service started","=="*15
    
    if ssl_conf.get('FAQ_SSL',False):
        http_server = HTTPServer(WSGIContainer(app), ssl_options = {
            "certfile":ssl_conf.get('FAQ_SSL_CERT'),
            "keyfile":ssl_conf.get('FAQ_SSL_KEY')
        })
    else:
        http_server = HTTPServer(WSGIContainer(app))
    
    http_server.bind(server_conf.get("PORT"))
    http_server.start(server_conf.get("FORKS"))
    IOLoop.current().start()
