#!/usr/bin/env python3
"""
Build script for the Lesson Portal
Processes YAML lesson files and generates static site
"""

import os
import json
import yaml
import shutil
from pathlib import Path
from jinja2 import Environment, FileSystemLoader, select_autoescape

import urllib.parse
from pathlib import PurePosixPath


# Shared instructor repository - same for all lessons
INSTRUCTOR_REPO = "act-cms/instructor-materials"  # Replace with your instructor repo

def load_yaml_file(filepath):
    """Load and parse a YAML file"""
    with open(filepath, 'r', encoding='utf-8') as f:
        return yaml.safe_load(f)

def get_lesson_id_from_filename(filename):
    """Extract lesson ID from YAML filename"""
    return Path(filename).stem

def process_lesson_data(lesson_data, lesson_id):
    """Process lesson data and add computed fields"""
    lesson_data['id'] = lesson_id
    
    # Add shared instructor repo
    lesson_data['instructor_repo'] = INSTRUCTOR_REPO
    
    # Automatically set instructor repo path to match lesson ID
    lesson_data['instructor_repo_path'] = lesson_id
    
    # Use fallback for instructor email if not specified
    if 'instructor_email' not in lesson_data:
        lesson_data['instructor_email'] = "N/A"
    
    # All lessons must now use the materials format with explicit URLs
    # Legacy formats (notebook/notebooks) are no longer supported
    if 'materials' not in lesson_data:
        if 'notebook' in lesson_data or 'notebooks' in lesson_data:
            print(f"Warning: Lesson {lesson_id} uses legacy format. Please convert to materials format with explicit URLs.")
            return None
        else:
            print(f"Error: Lesson {lesson_id} has no materials section.")
            return None

    # Generate chemcompute launch URLs from public_repo_url

    if "ChemCompute" in lesson_data["platforms"]:
        stub = "https://chemcompute.org/jupyterhub_internal/hub/user-redirect/git-pull?repo="

        # Lesson-level: opens the repo root folder
        repo_url = lesson_data['public_repo_url']
        parsed = urllib.parse.urlparse(repo_url)
        repo_stem = PurePosixPath(parsed.path).stem

        repo_url_encoded = urllib.parse.quote(repo_url)
        urlpath = f"lab/tree/{repo_stem}/"
        urlpath_encoded = urllib.parse.quote(urlpath)

        lesson_data['chemcompute_launch'] = (
            f"{stub}{repo_url_encoded}"
            f"&branch=main"
            f"&urlpath={urlpath_encoded}"
        )

        # Per-material: opens the specific notebook directly
        for material in lesson_data.get('materials', []):
            if material.get('type') == 'notebook' and 'github_url' in material:
                nb_parsed = urllib.parse.urlparse(material['github_url'])
                path_parts = nb_parsed.path.split('/blob/main/', 1)
                if len(path_parts) == 2:
                    mat_repo_url = f"{nb_parsed.scheme}://{nb_parsed.netloc}{path_parts[0]}"
                    notebook_path = path_parts[1]
                    mat_repo_stem = PurePosixPath(path_parts[0]).name
                    mat_urlpath = f"lab/tree/{mat_repo_stem}/{notebook_path}"
                    material['chemcompute_url'] = (
                        f"{stub}{urllib.parse.quote(mat_repo_url)}"
                        f"&branch=main"
                        f"&urlpath={urllib.parse.quote(mat_urlpath)}"
                    )
    
    return lesson_data

def load_paths(project_root):
    """Load learning paths from paths.yml if it exists; paths are optional"""
    paths_file = Path(project_root) / 'paths.yml'
    if not paths_file.exists():
        return []
    data = load_yaml_file(paths_file)
    if data is None:
        return []
    return data.get('paths', [])

def validate_paths(paths, lesson_ids):
    """Validate learning path definitions against known lesson IDs"""
    valid = True
    seen_ids = set()

    if not isinstance(paths, list):
        print("Error: paths.yml 'paths' must be a list")
        return False

    for i, path in enumerate(paths):
        label = f"paths.yml path {i+1}"
        if not isinstance(path, dict):
            print(f"Error: {label} must be a mapping")
            valid = False
            continue

        for field in ['id', 'title', 'description']:
            if not isinstance(path.get(field), str) or not path.get(field).strip():
                print(f"Error: {label} is missing a non-empty '{field}'")
                valid = False

        path_id = path.get('id')
        if path_id in seen_ids:
            print(f"Error: paths.yml has duplicate path id '{path_id}'")
            valid = False
        seen_ids.add(path_id)

        lessons = path.get('lessons')
        if not isinstance(lessons, list) or len(lessons) == 0 or not all(isinstance(l, str) for l in lessons):
            print(f"Error: {label} 'lessons' must be a non-empty list of lesson IDs")
            valid = False
            continue

        for lesson_id in lessons:
            if lesson_id not in lesson_ids:
                print(f"Error: {label} ('{path_id}') references unknown lesson '{lesson_id}'")
                valid = False
        if len(set(lessons)) != len(lessons):
            print(f"Error: {label} ('{path_id}') lists the same lesson more than once")
            valid = False

    return valid

def validate_cross_references(lessons_by_id):
    """Validate lesson-to-lesson references across all lessons.

    prerequisite_modules errors are fatal; related_modules issues are warnings
    only (existing data has known broken refs).
    """
    valid = True

    for lesson_id, lesson_data in lessons_by_id.items():
        prereqs = lesson_data.get('prerequisite_modules')
        if prereqs is not None:
            if not isinstance(prereqs, list) or not all(isinstance(p, str) for p in prereqs):
                print(f"Error: {lesson_id} prerequisite_modules must be a list of lesson IDs")
                valid = False
                continue
            for prereq in prereqs:
                if prereq == lesson_id:
                    print(f"Error: {lesson_id} lists itself in prerequisite_modules")
                    valid = False
                elif prereq not in lessons_by_id:
                    print(f"Error: {lesson_id} prerequisite_modules references unknown lesson '{prereq}'")
                    valid = False

        for module in lesson_data.get('related_modules', []):
            if isinstance(module, str) and module not in lessons_by_id:
                print(f"WARNING: {lesson_id} related_modules references unknown lesson '{module}'")

    if not valid:
        return False

    # Cycle detection over prerequisite_modules (iterative DFS)
    state = {}  # lesson_id -> 'visiting' | 'done'
    for start in lessons_by_id:
        if state.get(start) == 'done':
            continue
        stack = [(start, iter(lessons_by_id[start].get('prerequisite_modules') or []))]
        state[start] = 'visiting'
        path = [start]
        while stack:
            node, neighbors = stack[-1]
            advanced = False
            for neighbor in neighbors:
                if state.get(neighbor) == 'visiting':
                    cycle_start = path.index(neighbor)
                    cycle = ' -> '.join(path[cycle_start:] + [neighbor])
                    print(f"Error: circular prerequisite_modules detected: {cycle}")
                    return False
                if state.get(neighbor) != 'done':
                    state[neighbor] = 'visiting'
                    path.append(neighbor)
                    stack.append((neighbor, iter(lessons_by_id[neighbor].get('prerequisite_modules') or [])))
                    advanced = True
                    break
            if not advanced:
                state[node] = 'done'
                path.pop()
                stack.pop()

    return True

def annotate_lessons_with_paths(lessons, paths):
    """Add learning_paths and prerequisite_lessons fields to each lesson"""
    lessons_by_id = {lesson['id']: lesson for lesson in lessons}

    for lesson in lessons:
        lesson['learning_paths'] = []
        lesson['prerequisite_lessons'] = [
            {'id': prereq_id, 'title': lessons_by_id[prereq_id]['title']}
            for prereq_id in lesson.get('prerequisite_modules') or []
            if prereq_id in lessons_by_id
        ]

    for path in paths:
        path_lesson_ids = path['lessons']
        total = len(path_lesson_ids)
        for step, lesson_id in enumerate(path_lesson_ids, start=1):
            lesson = lessons_by_id.get(lesson_id)
            if lesson is None:
                continue
            prev_id = path_lesson_ids[step - 2] if step > 1 else None
            next_id = path_lesson_ids[step] if step < total else None
            lesson['learning_paths'].append({
                'path_id': path['id'],
                'path_title': path['title'],
                'step': step,
                'total': total,
                'prev': {'id': prev_id, 'title': lessons_by_id[prev_id]['title']} if prev_id else None,
                'next': {'id': next_id, 'title': lessons_by_id[next_id]['title']} if next_id else None,
            })

def build_lessons_json(lessons_dir, output_dir, paths):
    """Build the lessons.json file from all YAML files"""
    lessons = []

    # Process all YAML files in lessons directory
    for yaml_file in Path(lessons_dir).glob('*.yml'):
        print(f"Processing {yaml_file.name}...")

        lesson_data = load_yaml_file(yaml_file)
        lesson_id = get_lesson_id_from_filename(yaml_file.name)
        processed_lesson = process_lesson_data(lesson_data, lesson_id)

        if processed_lesson is not None:
            lessons.append(processed_lesson)
        else:
            print(f"Skipping {yaml_file.name} due to processing errors")

    # Add learning path memberships and resolved prerequisites
    annotate_lessons_with_paths(lessons, paths)

    # Sort lessons by title
    lessons.sort(key=lambda x: x['title'])
    
    # Write lessons.json
    output_file = Path(output_dir) / 'lessons.json'
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(lessons, f, indent=2, ensure_ascii=False)
    
    print(f"Generated {output_file} with {len(lessons)} lessons")
    return lessons

def build_lesson_pages(lessons, templates_dir, output_dir):
    """Build individual lesson pages from template"""
    
    # Setup Jinja2 environment
    env = Environment(
        loader=FileSystemLoader(templates_dir),
        autoescape=select_autoescape(['html', 'xml'])
    )
    
    # Load lesson template
    template = env.get_template('lesson.html')
    
    for lesson in lessons:
        print(f"Building lesson page for {lesson['id']}...")
        
        # Create lesson directory
        lesson_dir = Path(output_dir) / 'lessons' / lesson['id']
        lesson_dir.mkdir(parents=True, exist_ok=True)
        
        # Prepare template context - just lesson data
        context = lesson
        
        # Render template
        html_content = template.render(context)

        # Guard against unrendered Jinja making it into the published page
        for marker in ('{{', '{%', '{#'):
            if marker in html_content:
                idx = html_content.index(marker)
                snippet = html_content[idx:idx + 80].replace('\n', ' ')
                raise ValueError(
                    f"Lesson '{lesson['id']}' produced unrendered template syntax "
                    f"'{marker}' in its page: ...{snippet}..."
                )

        # Write lesson page
        lesson_file = lesson_dir / 'index.html'
        with open(lesson_file, 'w', encoding='utf-8') as f:
            f.write(html_content)
        
        print(f"Generated {lesson_file}")

def copy_static_files(source_dir, output_dir):
    """Copy index.html and any static assets"""
    
    # Copy index.html directly
    index_source = Path(source_dir) / 'index.html'
    index_dest = Path(output_dir) / 'index.html'

    css_source = Path(source_dir) / 'theme.css'
    css_dest = Path(output_dir) / 'theme.css'

    logo_source = Path(source_dir) / 'act-cms-logo.svg'
    logo_dest = Path(output_dir) / 'act-cms-logo.svg'
    
    if index_source.exists():
        shutil.copy2(index_source, index_dest)
        print(f"Copied {index_source} to {index_dest}")
    else:
        print(f"Warning: {index_source} not found")

    if css_source.exists():
        shutil.copy2(css_source, css_dest)
        print(f"Copied {css_source} to {css_dest}") 
    else:
        print(f"Warning: {css_source} not found")

    if logo_source.exists():
        shutil.copy2(logo_source, logo_dest)
        print(f"Copied {logo_source} to {logo_dest}")
    else:
        print(f"Warning: {logo_source} not found")   
    
    # Copy static directory if it exists
    static_source = Path(source_dir) / 'static'
    static_dest = Path(output_dir) / 'static'
    
    if static_source.exists():
        if static_dest.exists():
            shutil.rmtree(static_dest)
        shutil.copytree(static_source, static_dest)
        print(f"Copied static files from {static_source} to {static_dest}")

def get_platform_key(platform):
    """Compute the platform partial key (lowercase, spaces -> underscores)"""
    return platform.lower().replace(' ', '_')


def validate_lesson_data(lesson_data, filename, templates_dir=None):
    """Validate lesson data has required fields"""
    required_fields = [
        'title', 'description', 'programming_skill', 'primary_course',
        'authors', 'format', 'scientific_objectives',
        'cyberinfrastructure_objectives', 'platforms', 'materials',
        'public_repo_url'
    ]

    # Optional instructor fields that should be validated if present
    optional_instructor_fields = {
        'student_level': str,
        'students_piloted': (int, float),
        'instructor_notes': str,
        'related_modules': list,
        'prerequisite_modules': list
    }

    missing_fields = []
    for field in required_fields:
        if field not in lesson_data:
            missing_fields.append(field)

    if missing_fields:
        print(f"Error: {filename} is missing required fields: {missing_fields}")
        return False

    # Validate optional instructor fields if present (None == omitted)
    for field, expected_type in optional_instructor_fields.items():
        if field in lesson_data and lesson_data[field] is not None:
            value = lesson_data[field]
            if not isinstance(value, expected_type):
                print(f"Error: {filename} field '{field}' should be {expected_type.__name__ if hasattr(expected_type, '__name__') else expected_type}")
                return False

    # Fields the lesson template iterates over: a string where a list is
    # expected silently renders garbage (or crashes the build, in the case of
    # `platforms`). Require these to be non-empty lists of strings.
    required_list_fields = [
        'authors', 'scientific_objectives', 'cyberinfrastructure_objectives',
        'platforms'
    ]
    for field in required_list_fields:
        value = lesson_data[field]
        if not isinstance(value, list) or len(value) == 0:
            print(f"Error: {filename} field '{field}' must be a non-empty list "
                  f"(got {type(value).__name__}). Use YAML '- ' list items, not a single string.")
            return False
        if not all(isinstance(item, str) for item in value):
            print(f"Error: {filename} field '{field}' must be a list of strings")
            return False

    # Optional list-of-strings fields: only checked when present and non-null.
    optional_list_fields = [
        'also_for', 'tags', 'scientific_prerequisites', 'programming_prerequisites'
    ]
    for field in optional_list_fields:
        if field in lesson_data and lesson_data[field] is not None:
            value = lesson_data[field]
            if not isinstance(value, list) or not all(isinstance(item, str) for item in value):
                print(f"Error: {filename} field '{field}' must be a list of strings "
                      f"(got {type(value).__name__}). Use YAML '- ' list items, not a single string.")
                return False

    # Validate related_modules if present
    if 'related_modules' in lesson_data and lesson_data['related_modules'] is not None:
        if not all(isinstance(module, str) for module in lesson_data['related_modules']):
            print(f"Error: {filename} related_modules should be a list of strings")
            return False

    # Check for legacy formats and reject them
    if 'notebook' in lesson_data or 'notebooks' in lesson_data:
        print(f"Error: {filename} uses legacy notebook/notebooks format. Please convert to materials format with explicit URLs.")
        return False
    
    # Validate materials structure
    if not isinstance(lesson_data['materials'], list):
        print(f"Error: {filename} materials field must be a list")
        return False
    
    if len(lesson_data['materials']) == 0:
        print(f"Error: {filename} materials list cannot be empty")
        return False
    
    for i, material in enumerate(lesson_data['materials']):
        if not isinstance(material, dict):
            print(f"Error: {filename} material {i+1} must be a mapping with title/description/type/duration")
            return False

        required_material_fields = ['title', 'description', 'type', 'duration']
        for field in required_material_fields:
            if field not in material:
                print(f"Error: {filename} material {i+1} is missing required field: {field}")
                return False

        # Require at least one URL (github_url or colab_url)
        if 'github_url' not in material and 'colab_url' not in material:
            print(f"Error: {filename} material {i+1} must have either github_url or colab_url")
            return False

        # Validate URL format if present
        for url_field in ['github_url', 'colab_url']:
            if url_field in material:
                url = material[url_field]
                if not isinstance(url, str) or not url.startswith('http'):
                    print(f"Error: {filename} material {i+1} {url_field} must be a valid HTTP/HTTPS URL")
                    return False

        # objectives is iterated by the template; a string would render garbage
        if 'objectives' in material and material['objectives'] is not None:
            objectives = material['objectives']
            if not isinstance(objectives, list) or not all(isinstance(o, str) for o in objectives):
                print(f"Error: {filename} material {i+1} 'objectives' must be a list of strings "
                      f"(got {type(objectives).__name__})")
                return False

    # recommended_platform must be exactly one of the listed platforms
    if 'recommended_platform' in lesson_data and lesson_data['recommended_platform'] is not None:
        recommended = lesson_data['recommended_platform']
        if not isinstance(recommended, str):
            print(f"Error: {filename} recommended_platform must be a single platform name (string)")
            return False
        if recommended not in lesson_data['platforms']:
            print(f"Error: {filename} recommended_platform '{recommended}' must exactly match one entry "
                  f"in platforms {lesson_data['platforms']} (pick exactly one)")
            return False

    # Every platform must have a rendering partial, else the build crashes on it
    if templates_dir is not None:
        platforms_dir = Path(templates_dir) / 'platforms'
        for platform in lesson_data['platforms']:
            partial = platforms_dir / f"{get_platform_key(platform)}.html"
            if not partial.exists():
                supported = sorted(p.stem for p in platforms_dir.glob('*.html'))
                print(f"Error: {filename} platform '{platform}' is not supported "
                      f"(no template {partial.name}). Supported platform keys: {supported}")
                return False

    return True

def main():
    """Main build process"""
    print("Building Lesson Portal...")
    print("Note: Only materials format with explicit URLs is now supported.")
    
    # Define paths
    script_dir = Path(__file__).parent
    project_root = script_dir.parent
    
    lessons_dir = project_root / 'lessons'
    templates_dir = project_root / 'templates'
    output_dir = project_root / 'site'  # This will be pushed to gh-pages
    
    # Create output directory
    output_dir.mkdir(exist_ok=True)
    
    # Validate required directories exist
    if not lessons_dir.exists():
        print(f"Error: Lessons directory {lessons_dir} not found")
        return 1
    
    if not templates_dir.exists():
        print(f"Error: Templates directory {templates_dir} not found")
        return 1
    
    # Check for YAML files
    yaml_files = list(lessons_dir.glob('*.yml'))
    if not yaml_files:
        print(f"Error: No .yml files found in {lessons_dir}")
        return 1
    
    print(f"Found {len(yaml_files)} lesson files")
    
    # Validate all lesson files first
    valid_lessons = True
    lessons_by_id = {}
    for yaml_file in yaml_files:
        lesson_data = load_yaml_file(yaml_file)
        if not isinstance(lesson_data, dict):
            print(f"Error: {yaml_file.name} did not parse to a mapping of fields")
            valid_lessons = False
            continue
        if not validate_lesson_data(lesson_data, yaml_file.name, templates_dir):
            valid_lessons = False
        else:
            lessons_by_id[yaml_file.stem] = lesson_data

    if not valid_lessons:
        print("Error: Some lesson files have validation errors")
        print("Please fix the errors above and run the build again.")
        return 1

    # Load and validate learning paths (optional paths.yml)
    paths = load_paths(project_root)
    if not validate_paths(paths, set(lessons_by_id)):
        print("Error: paths.yml has validation errors")
        print("Please fix the errors above and run the build again.")
        return 1

    # Validate lesson-to-lesson references (prerequisite_modules, related_modules)
    if not validate_cross_references(lessons_by_id):
        print("Error: lesson cross-references have validation errors")
        print("Please fix the errors above and run the build again.")
        return 1

    try:
        # Build lessons.json
        lessons = build_lessons_json(lessons_dir, output_dir, paths)
        
        if len(lessons) == 0:
            print("Error: No valid lessons found after processing")
            return 1
        
        # Build individual lesson pages
        build_lesson_pages(lessons, templates_dir, output_dir)
        
        # Copy static files
        copy_static_files(project_root, output_dir)
        
        print(f"\n✅ Build complete! Site generated in {output_dir}")
        print(f"📄 Generated {len(lessons)} lesson pages")
        print(f"🔗 Lessons available at: /lessons/[lesson-id]/")
        
        return 0
        
    except Exception as e:
        print(f"❌ Build failed: {e}")
        import traceback
        traceback.print_exc()
        return 1

if __name__ == '__main__':
    exit(main())
