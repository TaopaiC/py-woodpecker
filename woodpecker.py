import requests
import time
import argparse
from urllib3.connectionpool import HTTPConnectionPool

parser = argparse.ArgumentParser(description='woodpecker')
parser.add_argument("--url", type=str, default='https://httpbin.org/get', help="url")
parser.add_argument("--start", type=int, default=20, help="interval start at (sec)")
parser.add_argument("--step", type=int, default=10, help="interval step (sec)")
args = parser.parse_args()
print(args)

s = requests.Session()

def patch_connectionpool():
  previous_get_conn = HTTPConnectionPool._get_conn
  def _new_get_conn(self, timeout=None):
    conn = previous_get_conn(self, timeout)
    print('[{}] [q: {}/{}] conn.id: {}'.format(time.time(), self.pool.qsize(), self.pool.maxsize, id(conn)))
    return conn
  HTTPConnectionPool._get_conn = _new_get_conn

patch_connectionpool()

def job():
  i = args.start
  while True:
    print('[{}] start'.format(time.time()))
    r = s.request('get', args.url)
    print('[{}] response code: {}'.format(time.time(), r.status_code))
    print('\n[{}] sleep {}'.format(time.time(), i))
    time.sleep(i)
    i = i + args.step

def job2():
  for i in range(1):
    print(' [{}] start'.format(time.time()))
    r = s.request('get', args.url)
    print(' [{}] response code: {}'.format(time.time(), r.status_code))
    time.sleep(1)

# t = threading.Thread(target = job2)
# t.start()

job()
