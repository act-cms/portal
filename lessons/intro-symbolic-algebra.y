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
  #Provide a more detailed description of your lesson here.
  #Explain the context, what students will accomplish, and how this
  #fits into broader molecular science education.
  #
  #You can use multiple paragraphs to fully describe the lesson scope
  #and learning experience.
  This lesson is meant to provide foundational skills with using Python
  libraries for symbolic mathematics to solve chemical problems. While this
  lesson was originally written as a foundational module for physical &
  biophysical chemistry students, the chemical problem solving exercises
  included in the lesson are posed at the general chemistry level.

# COURSE INFORMATION (REQUIRED)
# Choose ONE: "None", "Beginner", "Intermediate", "Advanced"
programming_skill: "Beginner"

# Examples: "Foundational Module", "Physical Chemistry", "Organic Chemistry", 
# "Inorganic Chemistry", "Analytical Chemistry", "Biochemistry", "Materials Science", "Other"
primary_course: "Foundational Module"

# List other courses where this lesson could be used (optional)
also_for:
  - "General Chemistry"
  - "Physical Chemistry"
  - "Biophysical Chemistry"
  - "Materials Science"

# List all authors
authors: 
  - "Dr. Dom Sirianni"

# Estimated total time for all materials
estimated_time: "2-3 hours"

# Choose ONE: "Single Notebook", "Multi-Part Materials Module", "Project-Based Module"
format: "Single Notebook"

# MATERIALS SECTION (REQUIRED)
# List each notebook/material in logical order
materials:
  - title: "Part 1: Introduction"
    description: "Brief description of what this notebook covers"
    type: "notebook"  # Usually "notebook", could be "slides", "dataset", etc.
    duration: "1 hour"
    
    # REQUIRED: Include at least one URL (preferably both)
    # Direct link to notebook file on GitHub
    github_url: 
    # Google Colab launch link (recommended for accessibility)
    colab_url: 
    
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
  - "Apply programming and the `algebra_with_sympy` library to symbolically solve chemical problems"

# What computational/programming skills will students develop?
cyberinfrastructure_objectives:
  - "Define algebraic variables and expressions using the `algebra_with_sympy` library"
  - "Manipulate algebraic expressions to solve for a single variable"
  - "Substitute numerical values and units to evaluate algebraic expressions"
  - "Use `algebra_with_sympy` to solve chemical problems at the first-year general chemical level"

# PREREQUISITES (REQUIRED)
# What science background do students need?
scientific_prerequisites:
  - "Familiarity with gas laws, chemical kinetics, and equilibrium at the general chemical level"

# What programming experience is assumed?
programming_prerequisites:
  # - "No prior programming experience required"
  - "Basic Python syntax (variables, loops, functions)"

# PLATFORM SUPPORT (REQUIRED)
# List platforms where you've tested your materials
platforms:
  #- "Google Colab"
  - "Local Installation"
  #- "ChemCompute"

# Which platform do you recommend for most users?
recommended_platform: "Local Installation"

# REPOSITORY URLS (REQUIRED)
# Link to the main repository students can clone
student_repo_url: 

# Link to instructor materials (zip file in private repo)
instructor_materials_url: 

# METADATA (REQUIRED)
# Tags help with searching - use relevant keywords
tags:
  - "python"
  - "symbolic-algebra"
  - "general-chemistry"

