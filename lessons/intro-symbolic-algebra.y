# lessons/your-lesson-name.yml
# 
# STARTER TEMPLATE FOR ACT-CMS LESSON PORTAL SUBMISSION
# Replace all placeholder text with your actual lesson information
# Remove any sections that don't apply to your lesson

# BASIC METADATA (REQUIRED)
# Use a clear, descriptive title that includes the main topic
title: "Introduction to Symbolic Algebra & Calculus in Python"

# Brief description for search results (1-2 sentences)
description: "Students will be introduced to the fundamentals of symbolic mathematical manipulations in Python."

# Longer description for the lesson page (use | for multi-line text)
expanded_description: |
  Provide a more detailed description of your lesson here.
  Explain the context, what students will accomplish, and how this
  fits into broader molecular science education.
  
  You can use multiple paragraphs to fully describe the lesson scope
  and learning experience.

# COURSE INFORMATION (REQUIRED)
# Choose ONE: "None", "Beginner", "Intermediate", "Advanced"
programming_skill: "Beginner"

# Examples: "Foundational Module", "Physical Chemistry", "Organic Chemistry", 
# "Inorganic Chemistry", "Analytical Chemistry", "Biochemistry", "Materials Science", "Other"
primary_course: "Physical Chemistry"

# List other courses where this lesson could be used (optional)
also_for:
  - "Biophysical Chemistry"
  - "Materials Science"

# List all authors
authors: 
  - "Dr. Dom Sirianni"

# Estimated total time for all materials
estimated_time: "2-3 hours"

# Choose ONE: "Single Notebook", "Multi-Part Materials Module", "Project-Based Module"
format: "Multi-Part Materials Module"

# MATERIALS SECTION (REQUIRED)
# List each notebook/material in logical order
materials:
  - title: "Part 1: Introduction"
    description: "Brief description of what this notebook covers"
    type: "notebook"  # Usually "notebook", could be "slides", "dataset", etc.
    duration: "1 hour"
    
    # REQUIRED: Include at least one URL (preferably both)
    # Direct link to notebook file on GitHub
    github_url: "https://github.com/your-org/your-lesson-repo/blob/main/01-intro.ipynb"
    # Google Colab launch link (recommended for accessibility)
    colab_url: "https://colab.research.google.com/github/your-org/your-lesson-repo/blob/main/colab-notebooks/01-intro.ipynb"
    
    # Learning objectives specific to this material
    objectives:
      - "Specific skill students will develop"
      - "Another concrete learning outcome"
      - "Third measurable objective"
  
  # Add more materials as needed
  - title: "Part 2: Advanced Topics"
    description: "Description of second notebook"
    type: "notebook"
    duration: "90 min"
    github_url: "https://github.com/your-org/your-lesson-repo/blob/main/02-advanced.ipynb"
    colab_url: "https://colab.research.google.com/github/your-org/your-lesson-repo/blob/main/colab-notebooks/02-advanced.ipynb"
    objectives:
      - "Advanced skill development"
      - "Application of concepts from Part 1"

# LEARNING OBJECTIVES (REQUIRED)
# What molecular science concepts will students learn?
scientific_objectives:
  - "Apply programming to solve chemical problems"
  - "Understand molecular property X through computational analysis"
  - "Interpret results of computational molecular science calculations"

# What computational/programming skills will students develop?
cyberinfrastructure_objectives:
  - "Write and execute Python code in Jupyter notebooks"
  - "Use library X to perform scientific calculations"
  - "Create visualizations of molecular data"
  - "Debug common programming errors"

# PREREQUISITES (REQUIRED)
# What science background do students need?
scientific_prerequisites:
  - "General chemistry"
  - "Basic understanding of molecular structure"

# What programming experience is assumed?
programming_prerequisites:
  - "No prior programming experience required"
  # OR: - "Basic Python syntax (variables, loops, functions)"

# PLATFORM SUPPORT (REQUIRED)
# List platforms where you've tested your materials
platforms:
  - "Google Colab"
  - "Local Installation"
  - "ChemCompute"

# Which platform do you recommend for most users?
recommended_platform: "Google Colab"

# REPOSITORY URLS (REQUIRED)
# Link to the main repository students can clone
student_repo_url: "https://github.com/your-org/your-lesson-repo"

# Link to instructor materials (zip file in private repo)
instructor_materials_url: "https://github.com/act-cms/instructor-materials/raw/main/your-lesson-name.zip"

# METADATA (REQUIRED)
# Tags help with searching - use relevant keywords
tags:
  - "python"
  - "molecular-dynamics"
  - "visualization"
  - "quantum-chemistry"  # Use appropriate scientific area tags

