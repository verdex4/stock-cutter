# Stock Cutter

A web application that solves the **NP-hard Cutting Stock Problem** using **linear programming**. It finds a cutting plan for linear materials that **minimizes waste** while promoting **balanced usage** of available stock materials.

## 🌐 Live Demo

Try the working version of the app here:  
👉 [https://stockcutter.onrender.com](https://stockcutter.onrender.com)

⚠️ **Note**: The app is hosted on **Render's free tier**, which comes with limitations:
- The service **sleeps after 15 minutes of inactivity**.
- The first request after sleep may take **45–60 seconds** to load (you’ll see Render’s loading screen).
- The URL uses the `onrender.com` domain due to free-tier hosting.
- Occasional delays or loading errors may occur due to resource constraints of the free plan.

## 📋 Project Overview

**Problem statement**: Cut available stock materials into required pieces such that:
- **Waste (leftover material) is minimized**,
- **Stock usage is distributed as evenly as possible** across available items.

**Technical approach**:  
The core algorithm leverages **PuLP**, a Python library for linear and integer linear programming. The frontend is built with **HTML + JavaScript**, and the backend is powered by the **Flask** web framework.

## 📝 Example Task
The warehouse contains workpieces with lengths of 1 and 2, with quantities of 100 and 150 respectively.
An order is received for lengths of 0.5 and 1 with quantities of 4 and 5 respectively.

**Solution**:

_Option 1_.

- From 2 workpieces (L=1), we cut 4 parts of 0.5 (no waste)
- From 5 workpieces (L=1), we get 5 parts of length 1.

We achieved a solution with no waste, but we used 7 workpieces of length 1 and zero workpieces of length 2.
This is not balanced.

_Option 2_.

- From 2 workpieces (L=1), we cut 4 parts of 0.5 (no waste)
- From 1 workpiece (L=1), we get 1 part of length 1.
- From 2 workpieces (L=2), we cut the remaining 4 parts of 1 (no waste)

**Total**:

- Waste: 0 - minimum
- Consumption: 3 workpieces of length 1, 2 workpieces of length 2 - even distribution

## ⭐ Key Features

- Minimizes cutting waste.
- Promotes balanced consumption of stock materials.
- Allows editing of stock lengths and quantities.
- Supports adding and removing stock items.
- Simple, intuitive UI with clear results.
- Real-time computation, no page reload needed.
- Works with any linear material: pipes, metal bars, wood, profiles, etc.

## 🚀 Installation

### Using pip

```bash
# Clone the repository
git clone https://github.com/verdex4/stock-cutter.git

# Navigate into the project directory
cd stock-cutter

# (Optional) Create and activate a virtual environment
# Windows
python -m venv venv
venv\Scripts\activate
# Linux/macOS
python3 -m venv venv
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Run the app (visit http://127.0.0.1:5000 in your browser)
python -m src.app
```

### Using conda

```bash
# Clone the repository
git clone https://github.com/verdex4/stock-cutter.git

# Navigate into the project directory
cd stock-cutter

# Create the conda environment
conda env create -f environment.yml

# Activate the environment
conda activate stock-cutter

# Run the app (visit http://127.0.0.1:5000)
python -m src.app
```

## 📁 Project Structure

```
└── 📁 stock-cutter
    ├── 📁 src
    │   ├── 📁 static  # Static assets (CSS, JS)
    │   │   ├── 📁 css
    │   │   │   └── 📄 style.css
    │   │   └── 📁 js
    │   │       └── 📄 script.js
    │   ├── 📁 templates
    │   │   └── 📄 index.html  # Main page
    │   ├── 📄 __init__.py  # Package initialization
    │   ├── 📄 algorithm.py  # Core solver logic (Cutting Stock algorithm)
    │   ├── 📄 app.py  # Flask application (routing & API)
    │   └── 📄 parser.py  # Input data parser
    ├── 📄 .gitignore
    ├── 📄 environment.yml
    ├── 📄 LICENSE
    ├── 📄 README_eng.md
    ├── 📄 README.md
    └── 📄 requirements.txt
```

## 📄 License

This project is licensed under the **MIT License**. See the [LICENSE](LICENSE) file for details.

-------------------------------------------------------------------------------------------------
