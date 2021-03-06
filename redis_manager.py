import redis
import yaml
import sys
import json
import logging

logging.basicConfig(format='%(asctime)s %(levelname)-8s %(message)s',stream=sys.stdout, level=logging.DEBUG, datefmt='%Y-%m-%d %H:%M:%S')
logging.getLogger("pika").propagate = False

"""
Get connector for redis
If you don't have redis, you can use redis on docker with follow steps.
Getting most recent redis image
shell
docker pull redis
docker run --name whaleshark-redis -d -p 6379:6379 redis
docker run -it --link whaleshark-redis:redis --rm redis redis-cli -h redis -p 6379
"""

class RedisMgr:

    def __init__(self):
        self.redis_con = None
        self.host = None
        self.port = None
        with open('config/config_server_develop.yaml', 'r') as file:
            config_obj = yaml.load(file, Loader=yaml.FullLoader)
            self.host = config_obj['iiot_server']['redis_server']['ip_address']
            self.port = config_obj['iiot_server']['redis_server']['port']

    def connect(self):
        """
        Get connector for redis
        If you don't have redis, you can use redis on docker with follow steps.
        Getting most recent redis image
        shell: docker pull redis

        docker pull redis
        docker run --name whaleshark-redis -d -p 6379:6379 redis
        docker run -it --link whaleshark-redis:redis --rm redis redis-cli -h redis -p 6379

        :param host: redis access host ip
        :param port: redis access port
        :return: redis connector
        """

        try:
            conn_params = {
                "host": self.host,
                "port": self.port,
            }
            self.redis_conn = redis.StrictRedis(**conn_params)
        except Exception as e:
            logging.error(str(e))

        return self.redis_conn

    def get_conn(self):
        return self.redis_conn

    def config_equip_desc(self):
        '''
        Configure redis for equipment sensor desc(sensor_cd)
        key : const sensor_cd
        value : dictionary or map has sensor_cd:sensor description
        :return: redis connector
        '''
        # self.redis_conn = None
        try:
            # redis_conn = self.connect_redis(address, port)
            facilities_dict = self.redis_conn.get('facilities_info')
            if facilities_dict is None:
                facilities_dict = {'TS0001': {
                    '0001': 'TS_VOLT1_(RS)',
                    '0002': 'TS_VOLT1_(ST)',
                    '0003': 'TS_VOLT1_(RT)',
                    '0004': 'TS_AMP1_(R)',
                    '0005': 'TS_AMP1_(S)',
                    '0006': 'TS_AMP1_(T)',
                    '0007': 'INNER_PRESS',
                    '0008': 'PUMP_PRESS',
                    '0009': 'TEMPERATURE1(PV)',
                    '0010': 'TEMPERATURE1(SV)',
                    '0011': 'OVER_TEMP'}
                }
                self.redis_conn.set('facilities_info', json.dumps(facilities_dict))

        except Exception as e:
            logging.error(str(e))

        return self.redis_conn

    def set(self, key, value):
        ret = False
        try:
            if type(value) is dict:
                value = json.dumps(value)
            self.redis_conn.set(key, value)
            ret = True
        except Exception as e:
            logging.error(str(e))
        return ret

    def get(self, key):
        ret = None
        try:
            ret = self.redis_conn.get(key)
        except Exception as e:
            logging.error(str(e))
        return ret
        

    