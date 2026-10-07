# CloudScout

CloudScout turns live technology-job listings into a beginner-friendly, role-aware career roadmap. Search for any role and location, add the skills you already have, and CloudScout shows the skills employers mention most in those returned descriptions, your likely skill gaps, and a practical learning order.

## The problem

It is hard for technology professionals to tell which skills are actually in demand for their target role. Job requirements change quickly, and reading listings one by one makes it difficult to see the bigger picture. CloudScout uses the current job market to make that information easier to understand.

## How it works

1. Enter a job role, location, and your current skills.
2. CloudScout searches live Google Jobs data through SerpApi.
3. It scans returned job descriptions using a transparent, rule-based technology skill catalog.
4. It counts how often each skill appears, compares those skills with your input, and ranks missing skills by demand.

## Main features

- Live technology-job search by free-form role and location.
- Job cards with title, company, location, description, and job link when available.
- Employer skill-demand counts and percentages with visual progress bars.
- Recognizes common programming, web, data, cloud, DevOps, security, and general technology skills, including Python, Java, JavaScript, React, SQL, Power BI, AWS, Docker, CI/CD, IAM, and GitHub.
- Normalizes common naming variations such as `GCP` and `Google Cloud Platform`.
- Shows skills you already have, complete skill gaps, and the top 10 learning priorities.
- Responsive single-page interface for desktop and mobile.

## Tech stack

- Python 3
- Flask
- Requests
- python-dotenv
- SerpApi Google Jobs API
- HTML and CSS

## SerpApi and live job data

SerpApi is the core data source for CloudScout. The app calls SerpApi's `google_jobs` engine with the selected role and location, then uses the returned job descriptions as the basis for its analysis. Without live job data, CloudScout could not identify what employers are asking for right now.

## Setup on Windows

### 1. Create and activate a virtual environment

Open PowerShell in the project folder:

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
```

If PowerShell prevents activation, you can run the virtual-environment Python executable directly in the later commands.

### 2. Install dependencies

```powershell
python -m pip install -r requirements.txt
```

### 3. Create your local environment file

Copy the example file:

```powershell
Copy-Item .env.example .env
```

Open `.env` and replace the placeholder with your SerpApi key:

```env
SERPAPI_KEY=your_real_serpapi_key
```

Never commit `.env`. It is already ignored by Git.

### 4. Run CloudScout

```powershell
.\.venv\Scripts\python.exe app.py
```

Then open [http://127.0.0.1:5000](http://127.0.0.1:5000) in your browser.

## Example search

- **Job role:** `Cloud Engineer` (or `Python Developer`, `Data Analyst`, and other technology roles)
- **Location:** `Bengaluru, Karnataka, India`
- **Your current skills:** `Python, Git`

The results page will display live jobs, skills employers mention, missing skills, and up to ten recommended learning priorities.

## Project structure

```text
CloudScout/
├── app.py                 # Flask routes, SerpApi request, and skill analysis
├── requirements.txt       # Required Python packages
├── .env.example           # Safe environment-variable template
├── .gitignore             # Excludes secrets and local/generated files
├── README.md              # Project documentation
└── templates/
    └── index.html         # Responsive CloudScout interface
```

## Limitations

- Results depend on the jobs returned by the current SerpApi search.
- The skill analysis only recognizes skills in its predefined catalog; it does not infer unlisted skills.
- A job may have an incomplete or missing description, which limits skill extraction for that listing.
- Search availability, job links, and result quality are controlled by the underlying Google Jobs data and SerpApi.
- This is a career-exploration aid, not a guarantee of hiring outcomes.

## AI assistance disclosure

CloudScout was developed with assistance from **OpenAI Codex**. AI assistance was used during development for code generation, debugging, testing guidance, UI refinement, and documentation drafting. The product's skill-analysis rules and project decisions were reviewed and implemented in this repository.
