# profile_opener.py
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium_stealth import stealth

def openProfile():
    # Create ChromeOptions
    chromeOptions = Options()

    # Optional: open Chrome in incognito mode
    chromeOptions.add_argument("--incognito")

    # Specify the user-data-dir and profile directory
    chromeOptions.add_argument("--user-data-dir=/Users/alexisguanique/Library/Application Support/Google/Chrome/SeleniumProfile7")
    chromeOptions.add_argument("--profile-directory=Profile 7")

    # Initialize the driver
    driver = webdriver.Chrome(options=chromeOptions)

    # Apply stealth settings
    stealth(
        driver,
        languages=["en-US", "en"],
        vendor="Google Inc.",
        platform="MacIntel",
        webgl_vendor="Intel Inc.",
        renderer="Intel Iris OpenGL Engine",
        fix_hairline=True,
    )

    # Return the driver to be used elsewhere
    return driver
