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
# None: No programming experience. 
# Beginner: Knows variables, conditionals, loops
# Intermediate: Can write their own scripts from scratch
# Advanced: Can write/develop software.

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

# Write a description of your module.
# Single notebook, multi-part module, etc?
format: "Single Notebook"

# INSTRUCTOR INFORMATION (OPTIONAL)
# Contact email for instructor access requests (optional - will use default if not specified)
instructor_email: "instructor-access@university.edu"
# Note: Instructor materials will be located at: instructor-repo/{lesson-filename}/
# where {lesson-filename} matches this YAML file's name

# INSTRUCTOR DETAILS (OPTIONAL)
# What level of students was this piloted with?
student_level: "Undergraduate - First Year & Beyond"  # e.g., "Graduate", "Undergraduate - First Year", "Mixed Graduate/Undergraduate"
# How many students has this been tested with?
students_piloted: 15  # Number of students
# Free-form notes for instructors
instructor_notes: |
  Additional context for instructors using this lesson:
  
  - This lesson works well when paired with a traditional lecture on molecular dynamics
  - Students often struggle with the concept of periodic boundary conditions in Part 2
  - The visualization exercises are very engaging - allow extra time for exploration
  - Consider assigning the dataset analysis as homework rather than in-class work
  
  Timing notes:
  - Part 1 typically takes students 45-60 minutes
  - Part 2 can be rushed in 90 minutes but is better with 2 hours
  
  Common student questions:
  - "I can solve these problems by hand, why do I need to use Python?" - remind students that later materials using calculus may be math they may not be able to do longhand

# Related lessons that complement this one
related_modules:
  - "foundational-intro-python"

# REPOSITORY URLS (REQUIRED)
# Link to the repository containing your public material
public_repo_url: "https://github.com/act-cms/your-lesson-repo"

# MATERIALS SECTION (REQUIRED)
# List each notebook/material in logical order
materials:
  - title: "Introduction to Symbolic Algebra in Python"
    description: "Brief description of what this notebook covers"
    type: "notebook"  # Usually "notebook", could be "slides", "dataset", etc.
    duration: "1.5 hours"
    
    # REQUIRED: Include at least one URL (preferably both)
    # Direct link to notebook file on GitHub
    github_url: "https://github.com/act-cms/your-lesson-repo/blob/main/01-intro.ipynb"
    # Google Colab launch link (recommended for accessibility)
    colab_url: "https://colab.research.google.com/github/act-cms/your-lesson-repo/blob/main/colab-notebooks/01-intro.ipynb"
    
    # Learning objectives specific to this material
    objectives:
      - "Define algebraic variables and expressions using the `algebra_with_sympy` library"
      - "Manipulate algebraic expressions to solve for a single variable"
      - "Substitute numerical values and units to evaluate algebraic expressions"
      - "Use `algebra_with_sympy` to solve chemical problems at the first-year general chemical level"

  #- title: "Introduction to Symbolic Calculus in Python"
  #  description: "Brief description of what this notebook covers"
  #  type: "notebook"  # Usually "notebook", could be "slides", "dataset", etc.
  #  duration: "1.5 hours"
  #  
  #  # REQUIRED: Include at least one URL (preferably both)
  #  # Direct link to notebook file on GitHub
  #  github_url: "https://github.com/act-cms/your-lesson-repo/blob/main/01-intro.ipynb"
  #  # Google Colab launch link (recommended for accessibility)
  #  colab_url: "https://colab.research.google.com/github/act-cms/your-lesson-repo/blob/main/colab-notebooks/01-intro.ipynb"
  #  
  #  # Learning objectives specific to this material
  #  objectives:
  #    - "Define algebraic variables and expressions using the `algebra_with_sympy` library"
  #    - "Manipulate algebraic expressions to solve for a single variable"
  #    - "Substitute numerical values and units to evaluate algebraic expressions"
  #    - "Use `algebra_with_sympy` to solve chemical problems at the first-year general chemical level"
  
# LEARNING OBJECTIVES (REQUIRED)
# What molecular science concepts will students learn?
scientific_objectives:
  - "Apply symbolic algebra in Python to solve general chemical problems"

# What computational/programming skills will students develop?
cyberinfrastructure_objectives:
  - "Define algebraic variables and expressions using the `algebra_with_sympy` library"
  - "Manipulate algebraic expressions to solve for a single variable"
  - "Substitute numerical values and units to evaluate algebraic expressions"
  - "Use `algebra_with_sympy` to solve chemical problems at the first-year general chemical level"

# PREREQUISITES (REQUIRED)
# What science background do students need?
scientific_prerequisites:
  - "General chemistry: gas laws, chemical kinetics, & equilibrium"

# What programming experience is assumed?
programming_prerequisites:
  - "Basic Python syntax (variables, loops, functions)"

# PLATFORM SUPPORT (REQUIRED)
# List platforms where your materials can be used.
platforms:
  #- "Google Colab"
  - "Local Installation"
  #- "ChemCompute"

# Which platform do you recommend for most users?
recommended_platform: "Local Installation"

# METADATA (REQUIRED)
# Tags help with searching - use relevant keywords
tags:
  - "python"
  - "symbolic-algebra"
  - "general-chemistry"
