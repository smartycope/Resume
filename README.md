# Resume Builder

A dynamic resume builder that allows you to build a resume from a set of pre-defined sections. It lets you fully seperate the content from the styling, and easily customize the content for the position. 

## Paths
- `resume_builder.py` - The main streamlit application to run
- `resume_config.json` - Pre-defined resumes to use as bases
- `data.json` - The data for all the resumes
- `icons.json` - The icons
- `base.html` - The base HTML file that the resume is built from. It gets filled with the data from `data.json` and `icons.json` using .format()
- `base.css` - The base CSS file

## Usage
Obviously, you'll want to customize with your own resume. You'll want to fill in data.json, customize your resume_config.json accordingly, and probably modify base.html and base.css to match your style.


Install dependencies:
```bash
pip install -r requirements.txt
```

Then run with streamlit:
```bash
streamlit run resume_builder.py
```
