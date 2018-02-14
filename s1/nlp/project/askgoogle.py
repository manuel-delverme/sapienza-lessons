import sys
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.chrome.options import Options
from disk_utils import disk_cache

chrome_options = Options()
chrome_options.add_argument("--window-size=1024x768")
chrome_options.add_argument("--headless")
driver = webdriver.Chrome("./chromedriver", chrome_options=chrome_options)


@disk_cache
def ask_google(_0, query, _1):
    # Search for query
    query = query.replace(' ', '+')

    driver.get('http://www.google.co.uk/search?q=' + query)

    x = 350
    y = 580
    answer = driver.execute_script("""return document.elementFromPoint(arguments[0], arguments[1]);""", x, y)
    # driver.get_screenshot_as_file("/tmp/{}-{}-{}.png".format(x, y, answer.text))
    driver.save_screenshot("/tmp/{}.png".format(query))
    # print(y, answer.text)

    if "\n" in answer.text:
        answer = answer.text.split("\n")[1]
        # if answer and "parigi" in answer.text.lower():
        #    break
        # else:
        if len(answer) < 100 and answer != "Traduci questa pagina":
            return answer

# print("answer:\n", ask_google(None, sys.argv[1]), None)
