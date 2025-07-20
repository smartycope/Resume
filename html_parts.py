import streamlit as st
from pathlib import Path
import jsonc

if 'loaded' not in st.session_state:
    st.stop()
CONFIG, SECTIONS, DATA, ICONS, CSS = st.session_state['loaded']

def head():
    return f"""
        <head>
            <meta charset="UTF-8">
            <meta name="viewport" content="width=device-width, initial-scale=1.0">
            <title>{DATA['name']} - Resume</title>
            <style>{CSS}</style>
        </head>
        """

def title(config):
    return f"""<div class="header">
            <h1 id="name">{DATA['name']}</h1>
            <h2 id="title">{config['title']}</h2>
        </div>"""

def section(title, content, bulletted=False, id=None):
    id = id or title.lower().replace(" ", "-")
    return f"""
        <div class="section" id="{id}-section">
            <h2>{title}</h2>
            {content}
        </div>
    """

def format_skill(skill, description):
    return f'<li><strong>{skill}</strong>: {description}</li>'

def format_soft_skill(skill, description):
    return f'<li><strong>{skill}</strong>: {description}</li>'

def format_reference(reference, info):
    return f'<li><strong>{reference}</strong>: {info}</li>'

def sub_section(main, subsection):
    """ Formats a single section of the resume """
    if main not in DATA:
        raise KeyError(f"Main section {main} not found in data")
    if subsection not in DATA[main]:
        raise KeyError(f"Subsection {subsection} not found in data")

    if 'desc' in DATA[main][subsection]:
        body = f'<p class="{main}-desc subsection-desc" id="{main}-{subsection}-desc">{DATA[main][subsection]["desc"]}</p>'
    elif 'bullets' in DATA[main][subsection]:
        body = f"""
            <ul class="{main}-bullets subsection-bullets" id="{main}-{subsection}-bullets">
                {'\n'.join(f"<li class=\"{main}-{subsection}-bullet {main}-bullet subsection-bullet\">{i}</li>" for i in DATA[main][subsection]["bullets"])}
            </ul>
        """
    else:
        body = ''
    return f'''
        <p class="{main} subsection" id="{main}-{subsection}">
            <strong id="{main}-{subsection}-title" class="{main}-title subsection-title">
                {DATA[main][subsection]['title']}
            </strong>
            <span id="{main}-{subsection}-subtitle" class="{main}-subtitle subsection-subtitle">
                {DATA[main][subsection].get('subtitle', '').format(**ICONS)}
            </span>
        </p>
        {body}
    '''

def skills(config):
    if 'skills' not in config:
        return ''
    content = f"""
        <ul class="skills-bullets">
            {'\n'.join(format_skill(skill, desc) for skill, desc in config['skills'].items())}
        </ul>
    """
    return content

def summary(config):
    if 'summary' not in config:
        return ''
    return config['summary']

def education(config):
    if 'education' not in config:
        return ''
    # content = ''
    # for school in config['education']:
    #     info = DATA['education'][school]
    #     content += f"""
    #         <p class="section-title">
    #             <strong>{DATA['education'][school]['name']}</strong>
    #             <span class="section-desc">{info.get('started', '')}{' - ' if info.get('ended') else ''}{info.get('ended', '')}</span><br>
    #         </p>
    #         <p style="font-style: italic;">{info.get('desc', '')}</p>
    #     """
    # if 'additional_education' in config:
    #     if type(config['additional_education']) is str:
    #         content += f"{config['additional_education']}"
    #     elif type(config['additional_education']) is list:
    #         content += f"""
    #             <ul>
    #                 {'\n'.join(f"<li>{i}</li>" for i in config['additional_education'])}
    #             </ul>
    #         """
    # return content
    return '\n'.join(sub_section('education', i) for i in config['education'])

def projects(config):
    if 'projects' not in config:
        return ''
    return '\n'.join(sub_section('projects', i) for i in config['projects'])

def jobs(config):
    if 'jobs' not in config:
        return ''
    return '\n'.join(sub_section('jobs', i) for i in config['jobs'])

def soft_skills(config):
    if 'soft_skills' not in config:
        return ''
    return f"""<ul class="soft-skills-bullets">{'\n'.join(format_soft_skill(i, DATA['soft_skills'][i]) for i in config['soft_skills'])}</ul>"""

def references(config):
    if 'references' not in config:
        return ''
    return '\n'.join(format_reference(i, DATA['references'][i]) for i in config['references'])

def sections(config):
    return '\n'.join(section(config['section_titles'][part], globals()[part](config)) for part in config['order'])

def contact_info(config):
    s = []
    if config['contact_info']['phone']:
        s.append(f'{ICONS.get("phone_icon", "")} {DATA.get("contact_info", {}).get("phone", "")}')
    if config['contact_info']['email']:
        s.append(f'{ICONS.get("email_icon", "")} <a href="mailto:{DATA.get("contact_info", {}).get("email", "")}">{DATA.get("contact_info", {}).get("email", "")}</a>')
    if config['contact_info']['github']:
        s.append(f'{ICONS.get("github_icon", "")} <a href="https://{DATA.get("contact_info", {}).get("github", "")}">{DATA.get("contact_info", {}).get("github", "")}</a>')
    if config['contact_info']['website']:
        s.append(f'{ICONS.get("website_icon", "")} <a href="https://{DATA.get("contact_info", {}).get("website", "")}">{DATA.get("contact_info", {}).get("website", "")}</a>')
    return f"""
        <div class="contact-info">
            {' | '.join(s)}
        </div>
    """

def generate_html(config):
    # print(config)
    return f"""
        <!DOCTYPE html>
        <html lang="en">
        {head()}
        <body>
            {ICONS.get('personal_icon', '')}
            {title(config)}
            {contact_info(config)}
            {sections(config)}
        </body>
        </html>"""