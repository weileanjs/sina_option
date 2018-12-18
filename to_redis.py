
import redis
from config import REDIS_CONFIG
class opition2redis():
    def __init__(self,):
        pool = redis.ConnectionPool(host = REDIS_CONFIG['host'], port = REDIS_CONFIG['port'],
                                    db=REDIS_CONFIG['db'],password=REDIS_CONFIG['password'])
        self.redis = redis.Redis(connection_pool = pool)
    def insert_hash(self, key, value,days):
        print(key, value,days)
        self.redis.hmset(key, value)
        self.redis.expire(key,(int(days)+1)*86400)

#     def flush_db(self,):
#         self.redis.flushdb()
#
# if __name__ == '__main__':
#     foo = opition2redis()
#     foo.flush_db()
