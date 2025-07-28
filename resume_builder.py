from pathlib import Path

import jsonc
import streamlit as st
from streamlit_pdf_viewer import pdf_viewer
from streamlit_sortables import sort_items

from file_handling import get_pdf, save
from SemVer import get_last_version


@st.cache_data
def load(setup_folder):
    setup_folder = Path(setup_folder).expanduser()
    config_path = setup_folder / 'configs.jsonc'
    data_path = setup_folder / 'data.jsonc'
    icons_path = setup_folder / 'icons.jsonc'
    css_path = setup_folder / 'base.css'
    CONFIG = jsonc.loads(config_path.read_text())
    SECTIONS = ['summary', 'skills', 'education', 'projects', 'jobs', 'soft_skills', 'references']
    DATA = jsonc.loads(data_path.read_text())
    ICONS = jsonc.loads(icons_path.read_text())
    CSS = Path('base.css').read_text()
    if css_path.exists():
        CSS += '\n\n' + css_path.read_text()
    return CONFIG, SECTIONS, DATA, ICONS, CSS

st.set_page_config(page_title="Resume Builder", page_icon=":memo:")

# The actual UI code
with st.sidebar:
    with st.expander('Setup', expanded=True):
        l, r = st.columns([.9, .2], vertical_alignment='bottom')

        setup_folder = l.text_input('Setup Folder', './Cope', key='data', help='The folder containing the configs.jsonc, data.jsonc, and icons.jsonc files')
        if r.button('Reload'):
            load.clear()

        if not setup_folder:
            st.stop()

        loaded = load(setup_folder)
        CONFIG, SECTIONS, DATA, ICONS, CSS = loaded
        st.session_state['loaded'] = loaded

        from html_parts import generate_html

        base = st.selectbox('Base', CONFIG.keys())
        CONFIG[base]['order'] = sort_items([
            {'header': 'Sections', 'items': [i for i in SECTIONS if i not in CONFIG[base]['order']]},
            {'header': 'Selected Sections', 'items': [i for i in CONFIG[base]['order'] if i in SECTIONS]}
        ], multi_containers=True)[1]['items']
        folder = st.text_input('Resume Save Folder', '~/Documents/Job Stuff/Resumes')
        new_version = get_last_version(folder).increment()
        default = f'{new_version}.{CONFIG[base].get("abbr", "")}'
        name = st.text_input('Filename', placeholder=default)
        if name.strip() == '':
            name = default
        name = f'Resumé {name}'.strip()

    with st.form('config'):
        config = CONFIG[base]

        config['title'] = st.text_input('Title', config.get('title'))

        config['section_titles'] = st.data_editor(config.get('section_titles', {}))

        "Contact Info"
        l, r = st.columns(2)
        with l:
            config['contact_info']['phone'] = st.checkbox('Phone', value=config.get('contact_info', {}).get('phone', False))
            config['contact_info']['email'] = st.checkbox('Email', value=config.get('contact_info', {}).get('email', False))
        with r:
            config['contact_info']['github'] = st.checkbox('Github', value=config.get('contact_info', {}).get('github', False))
            config['contact_info']['website'] = st.checkbox('Website', value=config.get('contact_info', {}).get('website', False))

        # Display only the ones we've specified, and in the order we specified (why not?)
        for section in config['order']:
            match section:
                case 'skills':
                    "Skills"
                    config['skills'] = st.data_editor(config.get('skills', {}))
                    if st.form_submit_button('Add Skill'):
                        skills = config.get('skills', {})
                        skills['tmp'] = ''
                        config['skills'] = skills
                        st.rerun()
                case 'summary':
                    config['summary'] = st.text_area('Summary', config.get('summary'))

                case 'projects':
                    config['projects'] = sort_items([
                        {'header': 'Projects', 'items': [i for i in DATA.get('projects', {}).keys() if i not in config.get('projects', [])]},
                        {'header': 'Selected Projects', 'items': config.get('projects', [])}
                    ], multi_containers=True)[1]['items']

                case 'jobs':
                    config['jobs'] = sort_items([
                        {'header': 'Jobs', 'items': [i for i in DATA.get('jobs', {}).keys() if i not in config.get('jobs', [])]},
                        {'header': 'Selected Jobs', 'items': config.get('jobs', [])}
                    ], multi_containers=True)[1]['items']

                case 'soft_skills':
                    config['soft_skills'] = sort_items([
                        {'header': 'Soft Skills', 'items': [i for i in DATA.get('soft_skills', {}).keys() if i not in config.get('soft_skills', [])]},
                        {'header': 'Selected Soft Skills', 'items': config.get('soft_skills', [])}
                    ], multi_containers=True)[1]['items']

                case 'education':
                    config['education'] = sort_items([
                        {'header': 'Education', 'items': [i for i in DATA.get('education', {}).keys() if i not in config.get('education', [])]},
                        {'header': 'Selected Education', 'items': config.get('education', [])}
                    ], multi_containers=True)[1]['items']
                    if 'additional_education' in config:
                        if type(config['additional_education']) is str:
                            add_ed = config['additional_education']
                        elif type(config['additional_education']) is list:
                            add_ed = '\n'.join(config['additional_education'])
                        else:
                            add_ed = ''
                        add_ed_input = st.text_area('Extra Education Line', add_ed)
                        add_ed_input = add_ed_input.strip().splitlines()
                        if len(add_ed_input) > 1:
                            config['additional_education'] = add_ed_input
                        elif len(add_ed_input) == 1:
                            config['additional_education'] = add_ed_input[0]
                        else:
                            config['additional_education'] = ''


                case 'references':
                    config['references'] = sort_items([
                        {'header': 'References', 'items': [i for i in DATA.get('references', {}).keys() if i not in config.get('references', [])]},
                        {'header': 'Selected References', 'items': config.get('references', [])}
                    ], multi_containers=True)[1]['items']

        st.form_submit_button('Generate Resume')

    html = generate_html(config)

    # if generate or reload_html:
        # st.session_state['html'] = {'text': html}

    # Edit the HTML directly, if necissary
    # with st.expander('Source'):
    #     st.warning('Resetting and updating isnt quite reliable yet. But this sorta works')
    #     html = code_editor(html,
    #         height="600px",
    #         lang="html",
    #         key='html',
    #         allow_reset=True,
    #     )['text'] or formatted

    pdf = get_pdf(html)

    # Download buttons
    l, r = st.columns(2, gap='small', vertical_alignment='bottom')
    save_type = l.selectbox('Type', ['Save PDF', 'Save HTML', 'Download PDF', 'Download HTML'], index=0)
    if r.button('Save'):
        match save_type:
            case 'Save PDF':
                save('pdf', pdf, folder, name)
            case 'Save HTML':
                save('html', html, folder, name)
            case 'Download PDF':
                st.download_button('Download PDF', pdf, f'{name}.pdf', 'application/pdf')
            case 'Download HTML':
                st.download_button('Download HTML', html, f'{name}.html', 'text/html')

    l, r = st.columns(2, gap='large')
    if l.button('Set as Canonical Version'):
        CONFIG[base] = config
        Path(f'{setup_folder}/configs.jsonc').write_text(jsonc.dumps(CONFIG, indent=4))
        st.rerun()

# Generate and show the PDF
pdf_viewer(pdf, height=800, pages_vertical_spacing=40, width=3000)
