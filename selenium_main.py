from selenium import webdriver
from selenium.webdriver.common.by import By

def down_vk(link):
    options = webdriver.ChromeOptions()
    options.add_argument("user-agent=Mozilla/5.0 (Windows NT 6.1) AppleWebKit/537.36 (KHTML, like Gecko)"
                             " Chrome/99.0.4844.51 Safari/537.36")
    driver = webdriver.Chrome(executable_path="selenium/chromedriver.exe", options=options)
    owner, id_video = link.split("video")[-1].split("%")[0].split("_")
    newlink = f"https://m.vk.com/video{owner}_{id_video}"

    driver.get(url=newlink)
    links = driver.find_elements(by=By.XPATH, value="//source[@type='video/mp4']")
    links = [link.get_attribute("src") for link in links]
    driver.quit()
    return links
