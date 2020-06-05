""" Config manager class"""
import os
import sys
import copy
import json
import logging
import requests
import traceback

sys.path.append(str(os.getcwd()))
# from share.crypto.AESCipher import AESCipher
logger = logging.getLogger(__name__)


# noinspection PyBroadException,PyBroadException
class ConfigManager(object):
    """ Load a config from a json file """

    def __init__(self):
        self.asd = 'asd'
        self.default_conf_file = './pdf_extraction/code_util/config/default_config.json'
        self.conf_file = './pdf_extraction/code_util/config/config.json'

    def load_config(self, key="all"):
        """ Load the config file """
        try:
            if key == "all":
                logger.info('Read [%s] config from %s', key, self.default_conf_file)
                return json.load(open(self.default_conf_file))
            elif key == "db":
                # remote_config = json.load(open(self.default_conf_file)).get("remote_config")
                remote_config = self.load_config(key="remote_config")

                db_config = self.override_config(key)

                if not remote_config.get("USE_REMOTE_CONFIG"):
                    return db_config
                else:
                    return self.update_db_config(db_config, remote_config)
            else:
                return self.override_config(key)

        except IOError:
            print 'An error occured trying to read the file ', self.default_conf_file

    def override_config(self, key):
        default_conf = json.load(open(self.default_conf_file)).get(key, {})
        conf = json.load(open(self.conf_file)).get(key, {})
        for key in conf.keys():
            default_conf[key] = conf[key]
        return default_conf

    def update_db_config(self, db_config, remote_config):
        """ fetch db config with remote mongo creds """

        try:
            host_url = remote_config.get("CONFIG_HOST") + remote_config.get("CONFIG_END_POINT")
            # print host_url
            file_path = remote_config.get("API_KEY_PATH")
            api_key = self.read_key_from_file(file_path)

            if not api_key:
                return db_config

            headers = {
                'apikey': api_key.strip(),
                'cache-control': 'no-cache'}

            response = requests.get(host_url, headers=headers, verify = remote_config.get('ENV_SSL_VERIFY', False))
            db_object = response.json().get("db", {})
            if "MONGO_URL" in db_object:
                mongo_uri = db_object.get("MONGO_URL")
            else:
                mongo_uri = "mongodb://" + db_object.get("userName") + ":" \
                            + db_object.get("password") + "@" + db_object.get("host") + ":" + str(db_object.get("port"))
            # print "##", mongo_uri
            local_db_config = copy.deepcopy(db_config)
            local_db_config["MONGO_URI"] = mongo_uri
            return local_db_config

        except Exception:
            logger.critical('Failed to to fetch mongo_uri from remote host, using local mongo_uri')
            logger.error(traceback.format_exc())
            return db_config

    @staticmethod
    def read_key_from_file(file_path):
        """ read file content """
        try:
            with open(file_path, 'r') as myfile:
                api_key = myfile.read()
            return api_key
        except:
            logger.critical('Failed to read api key from file %s', file_path)
            return None


if __name__ == "__main__":
    conf = ConfigManager()
    log_conf = conf.load_config(key='log')
    logging.basicConfig(
        format=log_conf.get("FORMAT_STRING"),
        filename=log_conf.get("DEBUG_LOG"),
        level=logging.DEBUG)
    logger = logging.getLogger(__name__)

    print json.dumps(conf.load_config(key='squid_proxy'), indent=2)