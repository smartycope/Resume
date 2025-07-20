import base64
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.print_page_options import PrintOptions
# This is my new favorite library
import chromedriver_autoinstaller
import streamlit as st

from pathlib import Path
import clipboard

# See https://www.selenium.dev/documentation/webdriver/interactions/print_page/ for more options
print_options = PrintOptions()
# Margin is handled in the body of the HTML (via CSS)
MARGIN = 0
print_options.margin_top = MARGIN
print_options.margin_bottom = MARGIN
print_options.margin_left = MARGIN
print_options.margin_right = MARGIN
# Force only the first page, just in case there's an empty page or something
# print_options.page_ranges = ["1"]
# print_options.scale = 0.5 # 0.1 to 2.0
print_options.shrink_to_fit = False

if 'driver_installed' not in st.session_state:
    chromedriver_autoinstaller.install()
    st.session_state['driver_installed'] = True

if 'driver' not in st.session_state:
    options = Options()
    options.binary_location = "/usr/bin/google-chrome"
    # make sure it's all in the background
    options.add_argument('--headless')
    options.add_argument("--disable-gpu")
    try:
        st.session_state['driver'] = webdriver.Chrome(service=Service(), options=options)
    except:
        st.error('Failed to initialize Chrome driver. See terminal for more details')
        st.stop()
driver = st.session_state['driver']


def get_pdf(html):
    html_path = Path('resume.html')
    html_path.write_text(html)

    # Use selenium to convert the HTML to PDF
    driver.get(f'file:///{html_path.absolute()}')
    return base64.b64decode(driver.print_page(print_options))

def save(type, data, folder, name):
    if type == 'pdf':
        Path(f'{folder}/{name}.pdf').expanduser().write_bytes(data)
    elif type == 'html':
        Path(f'{folder}/{name}.html').expanduser().write_text(data)
    st.success(f'Saved {name}.{type}')
    st.button('Copy filepath', on_click=clipboard.copy, args=(Path(f'{folder}/{name}.{type}').expanduser(),))