import requests
import time
import argparse
import threading
import rollbar
from urllib3.connectionpool import HTTPConnectionPool

DEFAULT_USER_AGENT = "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/103.0.0.0 Safari/537.36"

parser = argparse.ArgumentParser(description='woodpecker')
parser.add_argument("--url", type=str, default='https://httpbin.org/get', help="url")
parser.add_argument("--init", type=int, default=20, help="interval init at (sec)")
parser.add_argument("--step", type=int, default=10, help="interval step (sec)")
parser.add_argument("--job-enable", type=bool, default=False, help="enable 2nd threading job")
parser.add_argument("--job-init", type=int, default=20, help="for 2nd job, interval init at (sec)")
parser.add_argument("--job-step", type=int, default=10, help="for 2nd job, interval step (sec)")
parser.add_argument("--rollbar-token", type=str, help="set rollbar access token and enable rollbar")
parser.add_argument("--user-agent", type=str, default=DEFAULT_USER_AGENT, help="set user agent string")
args = parser.parse_args()
print(args)

def tprint(*args, **kwargs):
  print('[{:.6f}] {}'.format(time.time(), ' '.join(map(str, args))))


def patch_connectionpool():
  previous_get_conn = HTTPConnectionPool._get_conn
  def _new_get_conn(self, timeout=None):
    conn = previous_get_conn(self, timeout)
    tprint('[q: {}/{}] conn.id: {}'.format(self.pool.qsize(), self.pool.maxsize, id(conn)))
    return conn
  HTTPConnectionPool._get_conn = _new_get_conn

patch_connectionpool()

if args.rollbar_token:
  rollbar.init(args.rollbar_token)
  print('rollba inited')

  def rollbarWrapper(func):
    def wrapper():
      try:
        print('wrapper')
        return func()
      except KeyboardInterrupt:
        raise
      except:
        rollbar.report_exc_info()
        raise
    return wrapper
else:
  def rollbarWrapper(func):
    return func

s = requests.Session()

@rollbarWrapper
def job():
  i = args.init
  while True:
    tprint('start')
    s.cookies.clear()
    s.headers.update({ 'User-Agent': args.user_agent })
    r = s.request('get', args.url)
    tprint('response code: {}\n'.format(r.status_code))
    tprint('sleep {}'.format(i))
    time.sleep(i)
    i = i + args.step

@rollbarWrapper
def job2():
  i = args.job_init
  while True:
    tprint(' start')
    s.cookies.clear()
    s.headers.update({ 'User-Agent': args.user_agent })
    r = s.request('get', args.url)
    tprint(' response code: {}\n'.format(r.status_code))
    tprint(' sleep {}'.format(i))
    time.sleep(i)
    i = i + args.job_step

if args.job_enable:
  t = threading.Thread(target = job2)
  t.start()

job()
