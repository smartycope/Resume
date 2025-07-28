# Resume Builder

A dynamic resume builder that allows you to build a resume from a set of pre-defined sections. It lets you fully seperate the content from the styling, and easily customize the content for the position.

## Paths
The `setup_folder` is the folder that contains all the files that are used to build the resume. You can specify it in the sidebar.
- `resume_builder.py` - The main streamlit application to run
- `html_parts.py` - The HTML parts of the resume. You can change this if you want to change the HTML layout of the resume
- `<setup_folder>/configs.jsonc` - Pre-defined resumes to use as bases
- `<setup_folder>/data.jsonc` - The data for all the resumes
- `<setup_folder>/icons.jsonc` - The icons
- `<setup_folder>/base.css` - Any custom CSS to apply on top of the base CSS

## Usage
Obviously, you'll want to customize with your own resume. You'll want to fill in data.jsonc with your own information, customize your configs.jsonc accordingly, and if you want to change the style at all, add a base.css, and icons.jsonc to match your style.


Install dependencies:
```bash
pip install -r requirements.txt
```

Then run with streamlit:
```bash
streamlit run resume_builder.py
```

## Data
`data.json` stores things that don't change, that are applicable for any resume you make. It describes *you*, and is specific to each person

```jsonc
{
    // Required, your name goes at the top
    "name": "Copeland Carter",
    // Required, contact info that goes under the title
    "contact_info": {
        "phone": "(555) 555-5555",
        "email": "smartycope@gmail.com",
        "github": "github.com/smartycope",
        "website": "smartycope.org"
    },
    // Optional, projects to include
    "projects": {
        // All the keys are arbitrary, it's what they're called in the config, they're not in the resume itself
        "EZRegex": {
            // Required
            "title": "EZRegex",
            // Optional, the text on the right-most side of the subsection. You can use {icons} and HTML here, they get formatted
            "subtitle": "{ezregex_icon} <a href=\"https://ezregex.org\">ezregex.org</a>",
            // Optional bullets for the subsection
            "bullets": [
                "Developed EZRegex from scratch, a <strong>Python</strong> library that greatly simplifies Regular Expression syntax",
                "Includes a web frontend which hosts a suite of tools to aid the development of <strong>Regular Expressions</strong>",
            ]
        },
        "GeoDoodle": {
            "title": "GeoDoodle",
            "subtitle": "date - other date",
            // As an alternative to bullets, if you just specify a single string, it will be added as-is instead of as bullets
            "desc": "Developed a <strong>web app</strong> allowing users to create unique patterns on a graph paper-like interface"
        },
        // Add more projects!
    },
    // Optional, jobs to include
    "jobs": {
        // Exact same format as projects
        "Homestead": {
            "title": "Homestead Assisted Living",
            "subtitle": "Head of IT | April 2019 - September 2022",
            "bullets": [
                "Provided technical support and maintenance services for an assisted living center, successfully maintaining and improving the facility's infrastructure and IT systems over several years",
                "Had the patience of a saint setting up and teaching elderly residents how to use their technology"
            ]
        },
        // Add more jobs!
    },
    // Optional, your education goes here
    "education": {
        // Again, the keys are arbitrary and not shown on the resume, just in the config
        "BYUI": {
            // This also follows the same format as projects & jobs
            "title": "Brigham Young University - Idaho",
            "subtitle": "April 2019 - July 2024",
            "desc": "Graduated with a Bachelor's in <strong>Computer Engineering</strong> with a <strong>Machine Learning</strong> Certificate",
        },
    },
    // Optional, soft skills to include
    "soft_skills": {
        // These keys are *not* arbitrary, they are the names of the skills
        "Quick Learner": "Contributed meaningful JavaScript commits at Accendero after a single week of learning the language",
        // Add more!
    }
}

```

## Configs
Configs are specific to each resume you make. They describe what specifically goes on each resume. It's useful to have a couple base templates to tweak for each position. Configs, combined with data.json, describe all the non-stylistic information that goes on your resume.

```jsonc
{
    "Software Engineering": {
        // Optional, used for the filename
        "abbr": "se",
        // Required, title that goes under your name
        "title": "Software Engineer | Backend Developer",
        // Optional, contact info that goes under the title. The data itself is in data.json (as it's not likely to change)
        "contact_info": {
            "phone": true,
            "email": true,
            "github": true,
            "website": true
        },
        // Optional, projects to include
        "projects": [
            "EZRegex",
            "GeoDoodle",
            "Senior Project"
        ],
        // Optional, jobs to include
        "jobs": [
            "Acer",
            "Accendero"
        ],
        // Optional, soft skills to include
        "soft_skills": [
            "Quick Learner",
            "Technical Writing",
            "Honesty"
        ],
        // Optional, skills to include. This is a dict of all the information
        "skills": {
            "Languages": "Python, TypeScript, R, HTML/CSS",
            "CI/CD": "Git, Bash Scripting, Jira, Docker",
            "Backend": "Django, Databases, Linux, REST APIs",
            "Frontend": "React/JSX, UI/UX, GitHub Pages"
        },
        // Optional, education to include
        "education": [
            "BYUI"
        ],
        // Required, order the sections go in. A section can be specified, but if not in here, it won't be displayed
        "order": [
            "skills",
            "education",
            "projects",
            "jobs",
            "soft_skills"
        ],
        // Required, the actual names of the sections
        "section_titles": {
            "skills": "Skills",
            "projects": "Projects",
            "jobs": "Work Experience",
            "soft_skills": "Soft Skills",
            "education": "Education"
        },
        // Optional, any additional information to include after education. If a string, it will be added as-is. If a list, it will be added as a bullet point list
        "additional_education": ""
    },
    // Add others here
}
```

## Icons
Icons are stored in `icons.json`. And can be referenced elsewhere

```jsonc
{
    // Arbitrarily named keys, and any sort of HTML
    "github_icon": "<svg>...</svg>",
    "ezregex_icon": "<img src=\"...\">"
}
```

## Styling
Lots of classes. You can find them in the source code. I don't feel like describing them here.