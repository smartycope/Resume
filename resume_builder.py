from pathlib import Path
import streamlit as st
from streamlit_pdf_viewer import pdf_viewer
from code_editor import code_editor
import json
import base64
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.print_page_options import PrintOptions
# This is my new favorite library
import chromedriver_autoinstaller

# I copied these from the raw HTML of https://mui.com/material-ui/material-icons/, then modified the class attr
ICONS = json.loads(Path('icons.json').read_text())
CONFIG = json.loads(Path('resume_config.json').read_text())
DATA = json.loads(Path('data.json').read_text())

projects = DATA['projects']
jobs = DATA['jobs']
soft_skills = DATA['soft_skills']
CSS = Path('base.css').read_text()
HTML = Path('base.html').read_text()

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


if 'driver' not in st.session_state:
    options = Options()
    options.binary_location = "/usr/bin/google-chrome"
    # make sure it's all in the background
    options.add_argument('--headless')
    options.add_argument("--disable-gpu")
    st.session_state['driver'] = webdriver.Chrome(service=Service(), options=options)
driver = st.session_state['driver']

if 'driver_installed' not in st.session_state:
    chromedriver_autoinstaller.install()
    st.session_state['driver_installed'] = True

st.set_page_config(page_title="Resume Builder", page_icon=":memo:")

def format_section(section):
    """ Formats a single section of the resume """
    return f'''
    <p class="section-title"><strong>{section['title']}</strong> <span class="section-desc">{section['subtitle'].format(**ICONS)}</span></p>
    <ul>
    {'\n'.join(f'<li>{i}</li>' for i in section['bullets'])}
    </ul>
    '''

def format_skill(skill, description):
    return f'<li><strong>{skill}</strong>: {description}</li>'

def format_soft_skill(skill, description):
    return f'<p><strong>{skill}</strong>: {description}</p>'


# The actual UI code
with st.sidebar:
    # Config
    base = st.selectbox('Base', CONFIG.keys())
    with st.form('config'):
        title = st.text_input('Title', CONFIG[base]['title'])
        "Skills"
        skills = st.data_editor(CONFIG[base]['skills'], use_container_width=True)
        selected_projects = st.pills('Projects', list(projects.keys()), selection_mode='multi', default=CONFIG[base]['projects']) or []
        selected_jobs = st.pills('Jobs', list(jobs.keys()), selection_mode='multi', default=CONFIG[base]['jobs']) or []
        selected_soft_skills = st.pills('Soft Skills', list(soft_skills.keys()), selection_mode='multi', default=CONFIG[base]['soft_skills']) or []
        reset_html = st.form_submit_button('Generate Resume')

    # Generate the HTML
    formatted = HTML.format(
        css=CSS,
        title=title,
        projects='\n'.join(format_section(projects[i]) for i in selected_projects),
        jobs='\n'.join(format_section(jobs[i]) for i in selected_jobs),
        soft_skills_header='<h2>Soft Skills</h2>' if selected_soft_skills else '',
        soft_skills='\n'.join(format_soft_skill(i, soft_skills[i]) for i in selected_soft_skills),
        skills='\n'.join(format_skill(i, skills[i]) for i in skills),
        **ICONS
    )

    if reset_html:
        st.session_state['html'] = {'text': formatted}
        print('resetting')
        # st.session_state['html'] = formatted

    # Edit the HTML directly, if necissary
    with st.expander('Source'):
        st.warning('Resetting and updating isnt quite reliable yet. But this sorta works')
        html = code_editor(formatted,
            height="600px",
            lang="html",
            key='html',
            allow_reset=True,
        )['text'] or formatted

    # Save the HTML, then convert it to PDF
    html_path = Path('resume.html')
    html_path.write_text(html)

    # Use selenium to convert the HTML to PDF
    driver.get(f'file:///{html_path.absolute()}')
    pdf = base64.b64decode(driver.print_page(print_options))

    # Download buttons
    version = st.text_input('Version', '7.')
    l, r = st.columns(2, gap='small')
    l.download_button('Download PDF', pdf, f'My Resumé {version}.{CONFIG[base]["abbr"]}.pdf', 'application/pdf')
    r.download_button('Download HTML', html, f'My Resumé {version}.{CONFIG[base]["abbr"]}.html', 'text/html')

l, r = st.columns(2, gap='large')
if l.button('Set as Canonical Version'):
    CONFIG[base] = {
        'abbr': CONFIG[base]['abbr'],
        'title': title,
        'projects': selected_projects,
        'jobs': selected_jobs,
        'soft_skills': selected_soft_skills,
        'skills': skills
    }
    Path('resume_config.json').write_text(json.dumps(CONFIG, indent=4))
    st.rerun()

if r.button('Reset'):
    st.rerun()

# Generate and show the PDF
pdf_viewer(pdf, height=800, pages_vertical_spacing=100, width=3000)
