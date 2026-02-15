> **Note**
> This is the same document in all three repositories.

# README
Welcome to CareerVision, the Project Work of Group F.
In this document you will find:
- Structure of each repository used
- Instructions on how to set up and run the project
We hope this will give you a good rough understanding of the project and an easy way to get started.

Detailed explanations on functionality can be found in the project work report under 01_Documentation in the CareerVision repository and the functionality diagrams in 04_Functionality diagrams in the CareerVision repository.

### AI Use Declaration
Artificial Intelligence tools were used during the development of this project as supportive tools for coding assistance, documentation improvement, debugging, and general research.

AI systems were primarily used to:

- Generate example code snippets and boilerplate structures  
- Assist in explaining technical concepts  
- Support debugging and refactoring  
- Improve documentation clarity and structure  
- Provide suggestions for architecture and implementation approaches  

All AI-generated content was carefully reviewed, adapted, and validated before being integrated into the project. The final implementation decisions, system architecture, database design, and integration logic were independently developed and verified by the project authors.

AI tools were used as development aids and not as autonomous decision-makers. Responsibility for correctness, functionality, security, and compliance of the final system remains entirely with the authors of this project.


# Structure
Outlined below is the file-structure of all repositories in our project and what each section contains.
Work in three repositories, Front-End, Back-End and LLM.

## Front-End: CareerVision  
Repository: https://github.com/AntonAveryan/ProjectWork_TeamF
HTML, JavaScript and CSS files that facilitate user interaction.

```markdown
ProjectWork_TeamF/
│
├── 01_Documentation/  
│   └── Project documentation and written reports
│
├── 02_Tests/  
│   └── Files generated to test the functionality of code
│
├── 03_Presentations/  
│   └── PDF of presentations given throughout the project
│
├── 04_Functionality diagrams/  
│   └── Full diagrams laying out how the functions of our project work and interact with each other
│
├── core/  
│   └── Django app module files (init, admin, apps, models, tests, urls, views), defining front end endpoints
│
│   ├── static/  
│   │   └── Static files, delivered to the client exactly as stored
│   │
│   │   ├── core/  
│   │   │   └── JavaScript files (chat, favorites, login, positions) implementing user interaction, front end functions, styles.css building blocks used in html
│   │   │
│   │   └── images/  
│   │       └── favicon, in browser display icon
│   │
│   └── templates/  
│       └── HTML files (base, chat, favorites, how_it_works, landing, positions, pricing) creating the pages the user interacts with
│
├── DjangoProject/  
│   └── Django project configuration package (settings, urls, asgi, wsgi), endpoint connections, async support
│
├── Locale/  
│   └── Translation files used in i18n (de, kk, lv, pl, ru)
│
├── translationFunctions/  
│   └── Methods used to compile and update translations to be served in .mo format
│
├── manage.py  
│   └── project’s settings module, allows you to run administrative commands
│
└── README.md  
    └── Read me
```
## Back-End: project_work_back  
Repository: https://github.com/L3x1p/project_work_back
Main functionalities of the project, in Python.

```markdown
project_work_back/
│
├── 01_Documentation/  
│   └── Project documentation and written reports
│
├── 02_Tests/  
│   └── Files generated to test the functionality of code (full pipeline, llm, view database)
│
├── .gitignore  
│   └── Files and folders should not be tracked or committed to the repository
│
├── career_summarizer_service.py  
│   └── Extract information from PDF, call LLM
│
├── index.html  
│   └── Frontend interface for testing PDF extraction and backend communication
│
├── linkedin_scraper.py  
│   └── Call and search LinkedIn with given input content
│
├── main.py  
│   └── Database setup, configure end-points, call career_summarizer_service & linkedin_scraper
│
├── README.md  
│   └── Read me
│
└── requirements.txt  
    └── Make installing all necessary dependencies easier
```

## LLM: llm_project_work  
Repository: https://github.com/L3x1p/llm_project_work
LLM implementation and interaction in Python.

```markdown
llm_project_work/
│
├── 01_Documentation/  
│   └── Project documentation and written reports
│
├── 02_Tests/  
│   └── Files generated to test the functionality of code (client)
│
├── .gitignore  
│   └── Files and folders should not be tracked or committed to the repository
│
├── api_service.py  
│   └── LLM prompt functionality, configure end-points
│
├── download_model.py  
│   └── Function to support downloading an applicable LLM
│
├── main.py  
│   └── Base prompt and language detection
│
├── README.md  
│   └── Read me
│
├── requirements.txt  
│   └── Make installing all necessary dependencies easier
│
└── setup_github.ps1  
    └── PowerShell script that connects your local Git project to a new GitHub repository
```

# Setup
The steps to set up and run the project:
1. [Install packages](#1-install-packages)
2. [Database setup](#2-database-setup)
3. [Install the LLM](#3-install-the-llm)
4. [Set up API endpoints](#4-api-endpoints)
5. [Start servers](#5-start-servers)

## 1. Install packages
Install all packages as shown missing by the IDE. Also reference the requirements.txt files, which contain required dependencies and packages.

## 2. Database setup
PostgreSQL Quick Setup Guide

### 1. Install PostgreSQL
1. Download PostgreSQL from:
   [https://www.postgresql.org/download/](https://www.postgresql.org/download/)
2. Run the installer.
3. Keep default components selected.
4. Set a password for the `postgres` user (remember it).
5. Keep the default port `5432`.
6. Finish installation.
pgAdmin will be installed automatically.

### 2. Connect in pgAdmin
1. Open **pgAdmin**.
2. Expand:

   ```
   Servers → PostgreSQL
   ```
3. Enter the `postgres` password when prompted.

### 3. Create a Database
1. Right-click **Databases**.
2. Select **Create → Database**.
3. Set:

   * Database name: `project_work_db`
   * Owner: `postgres`
4. Click **Save**.

Make sure that you give the correct permissions, in the database you might have to set:
`ALTER USER [username] WITH PASSWORD [your_password]`

### 4. Update the DATABASE_URL String
In project_work_back main.py find DATABASE_URL with your database URL, which should be this with the given instructions:
```
postgresql://postgres:yourpassword@localhost:5432/project_work_db
```

## 3. Install the LLM

A simple command-line chat interface for running QWEN 3B models locally.

### Setup

#### 1. Install Dependencies

For GPU support (CUDA 12.1):
```bash
pip install llama-cpp-python --extra-index-url https://abetlen.github.io/llama-cpp-python/whl/cu121
```

For CPU only (slower):
```bash
pip install llama-cpp-python
```

#### 2. Download a Model

Download a 3.1B-3.2B model in GGUF format. Here are **working** options:

**Option 1: Qwen 2.5 3B Instruct (Recommended - Fast & Good Quality)**
```bash
pip install huggingface-hub
hf download Qwen/Qwen2.5-3B-Instruct-GGUF qwen2.5-3b-instruct-q4_k_m.gguf --local-dir .
```
Then update the default model name in `main.py` or run: `python main.py qwen2.5-3b-instruct-q4_k_m.gguf`

**Option 2: Phi-3 Mini 3.8B (Very Fast)**
```bash
hf download microsoft/Phi-3-mini-4k-instruct-gguf Phi-3-mini-4k-instruct-q4.gguf --local-dir .
```
Then run: `python main.py Phi-3-mini-4k-instruct-q4.gguf`

**Option 3: Browse HuggingFace**
- Visit: https://huggingface.co/models?search=gguf+3b
- Look for models with `q4_k_m` or `q4` quantization
- Download the `.gguf` file manually
- Run: `python main.py path/to/downloaded/model.gguf`

**Quantization Guide:**
- `Q4_K_M` - Recommended: Good quality/speed balance (~2-3GB)
- `Q4` - Faster, slightly lower quality (~2GB)
- `Q5_K_M` - Better quality, slightly slower (~3-4GB)
- `Q8` - Best quality, slower (~6GB)

#### 3. Run the Chat

```bash
python main.py
```

Or specify a custom model path:
```bash
python main.py path/to/your/model.gguf
```

### Usage

- Type your message and press Enter
- Type `quit`, `exit`, or `bye` to exit
- Type `clear` to clear conversation history
- Press Ctrl+C to interrupt

### System Requirements

- NVIDIA GPU with CUDA support (RTX 4070 Super recommended)
- CUDA toolkit installed
- ~4-6GB VRAM for 3B models (Q4 quantization)
- Python 3.8+

### Troubleshooting

**Model not found error:**
- Make sure you've downloaded a GGUF model file
- Place it in the same directory as `main.py` or provide the full path

**GPU not being used:**
- Verify CUDA is installed: `nvidia-smi`
- Reinstall with GPU support: `pip uninstall llama-cpp-python && pip install llama-cpp-python --extra-index-url https://abetlen.github.io/llama-cpp-python/whl/cu121`

**Out of memory:**
- Try a smaller quantization (Q4_K_S instead of Q4_K_M)
- Reduce `n_ctx` in the code (currently 4096)

## 4. API Endpoints
Make sure you correctly set up the API-endpoints in the repository.
In standard configuration, the endpoints should be set to:
- Front-End: http://localhost:8001
- Back-End: http://localhost:8000
- LLM: http://localhost:8002

Therefor the endpoints in the Front-End, to the following core\static\core must be set to the Back-End endpoint, as such:
- login.js : `const API_BASE_URL = 'http://localhost:8000';`
- chat.js : `const CHAT_API_BASE_URL = (typeof API_BASE_URL !== 'undefined') ? API_BASE_URL : 'http://localhost:8000';`
- favorites.js : `const FAVORITES_API_BASE_URL = (typeof API_BASE_URL !== 'undefined') ? API_BASE_URL : 'http://localhost:8000';`
- positions.js : `const JOBS_API_BASE_URL = (typeof API_BASE_URL !== 'undefined') ? API_BASE_URL : 'http://localhost:8000';`

Set the endpoint in the Back-End to the LLM:
- career_summarizer_service.py : `LLM_CHAT_API_URL = os.getenv("LLM_CHAT_API_URL", "http://localhost:8002")`

## 5. Start servers
Run the following commands in the terminal to start the entire system, and open the Front-End server in your browser:
- Front-End Start: `python manage.py runserver 8001`
- Back-End Start: `uvicorn main:app --reload`
- LLM Start: `python api_service.py`
