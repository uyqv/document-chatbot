import configparser


class CfgCommon(object):
    # Constants
    ELASTIC_CLOUD_PASSWORD = None
    OPENAI_API_KEY = None
    LLM_MODEL = None
    INDEX_NAME = None

    @classmethod
    def load_config(cls, config_file='common/config.ini'):
        config = configparser.ConfigParser()
        config.read(config_file)
        try:
            cls.ELASTIC_CLOUD_PASSWORD = config['DEFAULT']['ElasticCloudPassword']
            cls.INDEX_NAME = config['DEFAULT']['IndexName']
            cls.LLM_MODEL = config['DEFAULT']['LLMModel']
            cls.OPENAI_API_KEY = config['DEFAULT']['OpenAIAPIKey']
        except KeyError:
            raise KeyError(f"ElasticCloudPassword key not found in {config_file} under DEFAULT section")


CfgCommon.load_config()