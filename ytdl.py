from urllib.parse import unquote
import requests
import re
from urllib.request import urlopen
from bs4 import BeautifulSoup
import time
url = input("enter the youtube url of the video\n\n")
for i in range(5):
    start2 = time.time()
    req = requests.get(url)
    print("Time::Requests:%f" % (time.time()-start2))
    start = time.time()
    page = urlopen(url)
    print("Time::URLopen:%f" % (time.time()-start))
