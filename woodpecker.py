import requests
import time
import argparse
import threading
from urllib3.connectionpool import HTTPConnectionPool

parser = argparse.ArgumentParser(description='woodpecker')
parser.add_argument("--url", type=str, default='https://httpbin.org/get', help="url")
parser.add_argument("--init", type=int, default=20, help="interval init at (sec)")
parser.add_argument("--step", type=int, default=10, help="interval step (sec)")
parser.add_argument("--job-enable", type=bool, default=False, help="enable 2nd threading job")
parser.add_argument("--job-init", type=int, default=20, help="for 2nd job, interval init at (sec)")
parser.add_argument("--job-step", type=int, default=10, help="for 2nd job, interval step (sec)")
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
  i = args.init
  while True:
    print('[{}] start'.format(time.time()))
    r = s.request('get', args.url)
    print('[{}] response code: {}'.format(time.time(), r.status_code))
    print('\n[{}] sleep {}'.format(time.time(), i))
    time.sleep(i)
    i = i + args.step

def job2():
  i = args.job_init
  while True:
    print(' [{}] start'.format(time.time()))
    r = s.request('get', args.url)
    print(' [{}] response code: {}'.format(time.time(), r.status_code))
    print('\n[{}] sleep {}'.format(time.time(), i))
    time.sleep(i)
    i = i + args.job_step

if args.job_enable:
  t = threading.Thread(target = job2)
  t.start()

job()
