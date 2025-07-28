import streamlit as st
from pathlib import Path
import jsonc
from streamlit import session_state as ss

if 'loaded' not in ss or ss['loaded'] is None:
    st.stop()

# _, _, DATA, ICONS, _ = ss['loaded']
CSS = 4
ICONS = 3
DATA = 2

def head():
    return f"""
        <head>
            <meta charset="UTF-8">
            <meta name="viewport" content="width=device-width, initial-scale=1.0">
            <title>{ss['loaded'][DATA]['name']} - Resume</title>
            <style>{ss['loaded'][CSS]}</style>
        </head>
        """

def title(config):
    return f"""<div class="header">
            <h1 id="name">{ss['loaded'][DATA]['name']}</h1>
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
    data = ss['loaded'][DATA]
    if main not in data:
        raise KeyError(f"Main section {main} not found in data")
    if subsection not in data[main]:
        raise KeyError(f"Subsection {subsection} not found in data")

    if 'desc' in data[main][subsection]:
        body = f'<p class="{main}-desc subsection-desc" id="{main}-{subsection}-desc">{data[main][subsection]["desc"]}</p>'
    elif 'bullets' in data[main][subsection]:
        body = f"""
            <ul class="{main}-bullets subsection-bullets" id="{main}-{subsection}-bullets">
                {'\n'.join(f"<li class=\"{main}-{subsection}-bullet {main}-bullet subsection-bullet\">{i}</li>" for i in data[main][subsection]["bullets"])}
            </ul>
        """
    else:
        body = ''
    return f'''
        <p class="{main} subsection" id="{main}-{subsection}">
            <strong id="{main}-{subsection}-title" class="{main}-title subsection-title">
                {data[main][subsection]['title']}
            </strong>
            <span id="{main}-{subsection}-subtitle" class="{main}-subtitle subsection-subtitle">
                {data[main][subsection].get('subtitle', '').format(**ss['loaded'][ICONS])}
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
    return f"""<ul class="soft-skills-bullets">{'\n'.join(format_soft_skill(i, ss['loaded'][DATA]['soft_skills'][i]) for i in config['soft_skills'])}</ul>"""

def references(config):
    if 'references' not in config:
        return ''
    return '\n'.join(format_reference(i, ss['loaded'][DATA]['references'][i]) for i in config['references'])

def sections(config):
    return '\n'.join(section(config['section_titles'][part], globals()[part](config)) for part in config['order'])

def contact_info(config):
    data = ss['loaded'][DATA]
    s = []
    if config['contact_info']['phone']:
        s.append(f'{ss['loaded'][ICONS].get("phone_icon", "")} {data.get("contact_info", {}).get("phone", "")}')
    if config['contact_info']['email']:
        s.append(f'{ss['loaded'][ICONS].get("email_icon", "")} <a href="mailto:{data.get("contact_info", {}).get("email", "")}">{data.get("contact_info", {}).get("email", "")}</a>')
    if config['contact_info']['github']:
        s.append(f'{ss['loaded'][ICONS].get("github_icon", "")} <a href="https://{data.get("contact_info", {}).get("github", "")}">{data.get("contact_info", {}).get("github", "")}</a>')
    if config['contact_info']['website']:
        s.append(f'{ss['loaded'][ICONS].get("website_icon", "")} <a href="https://{data.get("contact_info", {}).get("website", "")}">{data.get("contact_info", {}).get("website", "")}</a>')
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
            {ss['loaded'][ICONS].get('personal_icon', '')}
            {title(config)}
            {contact_info(config)}
            {sections(config)}
        </body>
        </html>"""