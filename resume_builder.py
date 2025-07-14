from pathlib import Path
import streamlit as st
from streamlit_pdf_viewer import pdf_viewer
from code_editor import code_editor
import base64
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.print_page_options import PrintOptions
# This is my new favorite library
import chromedriver_autoinstaller
import jsonc
import re
import clipboard

# I copied these from the raw HTML of https://mui.com/material-ui/material-icons/, then modified the class attr
ICONS = jsonc.loads(Path('icons.jsonc').read_text())
CONFIG = jsonc.loads(Path('resume_config.jsonc').read_text())
DATA = jsonc.loads(Path('data.jsonc').read_text())

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
    return f'<li><strong>{skill}</strong>: {description}</li>'

def generate_contact_section(phone, email, github, website):
    s = []
    if phone:
        s.append(f'{ICONS["phone_icon"]} (208) 513-0110')
    if email:
        s.append(f'{ICONS["email_icon"]} <a href="mailto:smartycope@gmail.com">smartycope@gmail.com</a>')
    if github:
        s.append(f'{ICONS["github_icon"]} <a href="https://github.com/smartycope">github.com/smartycope</a>')
    if website:
        s.append(f'{ICONS["website_icon"]} <a href="https://smartycope.org">smartycope.org</a>')
    return ' | '.join(s)

class SemVer:
    """ Semantic Versioning """
    def __init__(self, text):
        s = text.split('.')
        self.major, self.minor, self.patch = int(s[0]), int(s[1]), int(s[2])
    def __gt__(self, other):
        if self.major > other.major:
            return True
        elif self.major == other.major and self.minor > other.minor:
            return True
        elif self.major == other.major and self.minor == other.minor and self.patch > other.patch:
            return True
        return False
    def __eq__(self, other):
        return self.major == other.major and self.minor == other.minor and self.patch == other.patch
    def __str__(self):
        return f'{self.major}.{self.minor}.{self.patch}'
    def __hash__(self):
        return hash((self.major, self.minor, self.patch))
    __repr__ = __str__

    @staticmethod
    def extract(text):
        match = re.search(r'.*(\d+\.\d+\.\d+).*', text)
        if match:
            return SemVer(match.group(1))
        return None

    def increment(self, amt=1):
        self.patch += amt
        return self

def get_last_version(folder):
    versions = [SemVer.extract(pdf.name) for pdf in Path(folder).expanduser().glob('*.pdf')]
    versions = [v for v in versions if v is not None]
    return max(versions, default=SemVer('0.0.0'))


# The actual UI code
with st.sidebar:
    # Config
    base = st.selectbox('Base', CONFIG.keys())
    with st.form('config'):
        title = st.text_input('Title', CONFIG[base]['title'])
        "Contact Info"
        l, r = st.columns(2)
        with l:
            phone = st.checkbox('Phone', value=CONFIG[base]['contact_info']['phone'])
            email = st.checkbox('Email', value=CONFIG[base]['contact_info']['email'])
        with r:
            github = st.checkbox('Github', value=CONFIG[base]['contact_info']['github'])
            website = st.checkbox('Website', value=CONFIG[base]['contact_info']['website'])
        "Skills"
        skills = st.data_editor(CONFIG[base]['skills'], use_container_width=True)
        if st.form_submit_button('Add Skill'):
            skills = CONFIG[base]['skills']
            skills['tmp'] = ''
            CONFIG[base]['skills'] = skills
            st.rerun()
        # I like pills more, but they're not ordered
        # selected_projects = st.pills('Projects', list(projects.keys()), selection_mode='multi', default=CONFIG[base]['projects']) or []
        # selected_jobs = st.pills('Jobs', list(jobs.keys()), selection_mode='multi', default=CONFIG[base]['jobs']) or []
        # selected_soft_skills = st.pills('Soft Skills', list(soft_skills.keys()), selection_mode='multi', default=CONFIG[base]['soft_skills']) or []
        selected_projects = st.multiselect('Projects', list(projects.keys()), default=CONFIG[base]['projects']) or []
        selected_jobs = st.multiselect('Jobs', list(jobs.keys()), default=CONFIG[base]['jobs']) or []
        selected_soft_skills = st.multiselect('Soft Skills', list(soft_skills.keys()), default=CONFIG[base]['soft_skills']) or []
        additional_education = st.text_area('Additional Education', CONFIG[base].get('additional_education', ''))
        reset_html = st.form_submit_button('Generate Resume')

    if not len(selected_projects):
        CSS += '\n#experience-section { display: none; }'
    if not len(selected_jobs):
        CSS += '\n#work-experience-section { display: none; }'
    if not len(selected_soft_skills):
        CSS += '\n#soft-skills-section { display: none; }'



    # Generate the HTML
    formatted = HTML.format(
        css=CSS,
        additional_education=additional_education,
        contact_section=generate_contact_section(phone, email, github, website),
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
    folder = st.text_input('Folder', '~/Documents/Job Stuff/Resumes')
    new_version = get_last_version(folder).increment()
    default = f'{new_version}.{CONFIG[base]["abbr"]}'
    name = st.text_input('Filename', placeholder=default)
    if name == '':
        name = default

    name = f'Resumé {name}'.strip()
    l, r = st.columns(2, gap='small')
    if l.button('Save PDF'):
        Path(f'{folder}/{name}.pdf').expanduser().write_bytes(pdf)
        st.success(f'Saved {name}.pdf')
        st.button('Copy filepath', on_click=clipboard.copy, args=(Path(f'{folder}/{name}.pdf').expanduser(),))

    if r.button('Save HTML'):
        Path(f'{folder}/{name}.html').expanduser().write_text(html)
        st.success(f'Saved {name}.html')
        st.button('Copy filepath', on_click=clipboard.copy, args=(Path(f'{folder}/{name}.html').expanduser(),))

    l.download_button('Download PDF', pdf, f'{name}.pdf', 'application/pdf')
    r.download_button('Download HTML', html, f'{name}.html', 'text/html')


l, r = st.columns(2, gap='large')
if l.button('Set as Canonical Version'):
    CONFIG[base] = {
        'abbr': CONFIG[base]['abbr'],
        'title': title,
        'contact_info': {
            'phone': phone,
            'email': email,
            'github': github,
            'website': website
        },
        'projects': selected_projects,
        'jobs': selected_jobs,
        'soft_skills': selected_soft_skills,
        'skills': skills,
        'additional_education': additional_education
    }
    Path('resume_config.jsonc').write_text(jsonc.dumps(CONFIG, indent=4))
    st.rerun()

if r.button('Reset'):
    st.rerun()

# Generate and show the PDF
pdf_viewer(pdf, height=800, pages_vertical_spacing=40, width=3000)
