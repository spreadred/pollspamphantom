from selenium import webdriver
import threading, logging, sys

# config vars
maxVotes = 10000
maxVotesPerIP = 10
maxThreads = 10
lock = threading.Lock()
proxyFile = "proxy.txt"
currentProxyIndex = 0
currentVotes = 0

# set up logging
log = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO)

# hard worker
def worker():
    # slack
    global lock
    global proxies
    global currentProxyIndex
    global currentVotes
    global maxVotesPerIP
    global maxVotes
    global log
    
    lock.acquire()
    log.debug("Creating PhantomJS command line arguments")
    service_args = [
                        "--proxy={0}".format(proxies[currentProxyIndex]),
                        "--load-images=false",
                        ]
    
    log.debug("Arguments: {0}".format(service_args))
    log.info("Using proxy: {0}".format(service_args[0]))
    currentProxyIndex +=1
    lock.release()
            
    # init phantomjs webdriver and proxy
    try:
        log.debug("Creating PhantomJS webdriver instance.")
        driver = webdriver.PhantomJS(service_args=service_args)
        
        # set load timeout to 45 seconds, too high?
        driver.set_page_load_timeout(45)

        attempts = 0;

        while attempts < maxVotesPerIP and currentVotes < maxVotes:                
            attempts += 1
            
            driver.get("http://keepers.bracketeers.com")
            
            driver.execute_script("document.getElementById('checkboxFourInput_3078').click();")
            driver.execute_script("document.getElementsByClassName('btn-special')[1].click();")
    
            lock.acquire()
            currentVotes += 1
            log.info("Fabricated votes: {0}".format(currentVotes))
            lock.release()        
    except:
        # fucking exceptions
        e = sys.exc_info()[0]
        log.error(e)
    finally:
        log.debug("Shutting down PhantomJS webdriver instance.")
        driver.quit()

# get us some dem dere proxies
proxies = []
log.info("Parsing proxy list...")
try:
    with open(proxyFile) as f:
        proxies = f.read().splitlines()
except:
    sys.exit(sys.exc_info()[0])        
    
# spawning additional overlords
threads = []
while currentVotes < maxVotes:
    while len(threads) < maxThreads:
        t = threading.Thread(target=worker)
        threads.append(t)
        t.start()
        log.debug("Thread #{0} started.".format(len(threads)))
     

