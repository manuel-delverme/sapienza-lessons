import sys
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.chrome.options import Options

chrome_options = Options()
chrome_options.add_argument("--window-size=1024x768")
chrome_options.add_argument("--headless")
driver = webdriver.Chrome("./chromedriver", chrome_options=chrome_options)

def ask_google(query):
    # Search for query
    query = query.replace(' ', '+')

    driver.get('http://www.google.com/search?q=' + query)

    x = 350
    y = 580
    answer = driver.execute_script("""return document.elementFromPoint(arguments[0], arguments[1]);""", x, y)
    # driver.get_screenshot_as_file("/tmp/{}-{}-{}.png".format(x, y, answer.text))
    print(y, answer.text)
    # if answer and "parigi" in answer.text.lower():
    #    break
    # else:
    y += 10
    return answer.text

print("answer:\n", ask_google(sys.argv[1]))
