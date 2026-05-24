import os
import json

# Path to colleges dataset
DATA_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'data')
COLLEGES_FILE = os.path.join(DATA_DIR, 'colleges.json')

def load_colleges():
    if os.path.exists(COLLEGES_FILE):
        with open(COLLEGES_FILE, 'r', encoding='utf-8') as f:
            return json.load(f)
    return []

def determine_stream(career):
    """
    Strictly maps a predicted career to its primary stream.
    Used for filtering colleges that are relevant to that career.
    """
    career_lower = career.lower()

    # Biotechnology / Biomedical / Bioinformatics → Science (BSc Biotechnology is primarily a Science degree)
    if any(kw in career_lower for kw in ['biotechnolog', 'biomedic', 'bioinformatic']):
        return "Science"

    # Pharmacist / Pharmaceutical → Medical
    if any(kw in career_lower for kw in ['pharmacist', 'pharmaceutical']):
        return "Medical"

    # Pure Engineering / Tech careers
    if any(kw in career_lower for kw in [
        'software engineer', 'hardware engineer', 'civil engineer', 'mechanical engineer',
        'electrical engineer', 'chemical engineer', 'aerospace engineer', 'robotics engineer',
        'developer', 'architect', 'data scientist', 'data analyst', 'cybersecurity',
        'network engineer', 'cloud engineer', 'ai engineer', 'ml engineer', 'machine learning',
        'computer scientist', 'it specialist'
    ]):
        return "Engineering"

    # Generic "engineer" or "technology" keywords (not bio)
    if 'engineer' in career_lower and 'biomedic' not in career_lower:
        return "Engineering"
    if 'technolog' in career_lower and 'biotechnolog' not in career_lower:
        return "Engineering"

    # Medical / Healthcare careers
    if any(kw in career_lower for kw in [
        'doctor', 'surgeon', 'physician', 'dentist', 'nurs', 'medic',
        'radiolog', 'patholog', 'anesthesiolog', 'psychiatrist', 'physiotherapist',
        'veterinar', 'ayurved'
    ]):
        return "Medical"

    # Commerce / Business / Finance careers
    if any(kw in career_lower for kw in [
        'account', 'financ', 'chartered accountant', 'ca ', 'business', 'manag',
        'market', 'bank', 'commerce', 'hr ', 'human resource', 'entrepreneur',
        'investment', 'stock', 'economist', 'actuar', 'insurance', 'logistics',
        'supply chain', 'retail', 'e-commerce'
    ]):
        return "Commerce"

    # Arts / Humanities / Social Sciences
    if any(kw in career_lower for kw in [
        'psycholog', 'journalist', 'writer', 'content creator', 'teacher', 'educat',
        'social work', 'law', 'lawyer', 'legal', 'historian', 'political scientist',
        'philosopher', 'anthropolog', 'linguist', 'artist', 'designer', 'fashion',
        'music', 'film', 'media', 'public relation', 'counsellor', 'counselor',
        'sociolog', 'librar', 'archaeolog', 'humanities', 'arts stream'
    ]):
        return "Arts"

    # Pure Science / Research
    if any(kw in career_lower for kw in ['scientist', 'researcher', 'research', 'science', 'physics', 'chemistry', 'biology', 'mathematics', 'statistician']):
        return "Science"

    return "Any"


def get_required_course_keywords(career, standard):
    """
    Returns the list of course keywords that a college MUST offer
    to be relevant for the predicted career and standard.
    """
    career_lower = career.lower()

    if standard == "10th":
        # For 10th → junior college stream selection
        if any(kw in career_lower for kw in [
            'software', 'engineer', 'data scientist', 'data analyst', 'developer',
            'architect', 'civil', 'mechanical', 'electrical', 'aerospace', 'robotics',
            'cybersecurity', 'network', 'cloud', 'ai ', 'ml ', 'machine learning',
            'technolog', 'computer'
        ]):
            return ["PCM", "Science (PCM)", "Science"]  # Must have PCM science

        if any(kw in career_lower for kw in [
            'doctor', 'surgeon', 'medic', 'nurs', 'dentist', 'pharmacist',
            'biotechnolog', 'biomedic', 'physiotherapist', 'veterinar', 'ayurved',
            'physician', 'radiolog', 'patholog'
        ]):
            return ["PCB", "Science (PCB)", "Science"]  # Must have PCB science

        if any(kw in career_lower for kw in [
            'account', 'financ', 'business', 'manag', 'market', 'bank',
            'commerce', 'hr', 'entrepreneur', 'ca ', 'economist', 'actuar',
            'investment', 'stock'
        ]):
            return ["Commerce"]

        if any(kw in career_lower for kw in [
            'psycholog', 'journalist', 'writer', 'teacher', 'educat',
            'social work', 'law', 'lawyer', 'historian', 'political',
            'philosopher', 'sociolog', 'artist', 'designer', 'media',
            'content creator', 'librar', 'archaeolog', 'linguist',
            'art', 'humanit', 'humanities', 'arts stream'
        ]):
            return ["Arts"]

        # Default for 10th: return PCM science as fallback for Engineering/Science predicted paths
        return ["PCM", "Science"]

    else:
        # For 12th → undergraduate course selection
        if any(kw in career_lower for kw in ['software', 'developer', 'computer scientist', 'it ']):
            return ["CS", "IT", "Computer", "BSc Computer Science", "BSc CS"]

        if any(kw in career_lower for kw in ['data scientist', 'data analyst', 'machine learning', 'ai engineer', 'ml engineer']):
            return ["CS", "IT", "Mathematics", "BSc Mathematics", "BSc Computer Science", "Statistics"]

        if any(kw in career_lower for kw in ['civil engineer']):
            return ["Civil", "Architecture"]

        if any(kw in career_lower for kw in ['mechanical engineer']):
            return ["Mechanical"]

        if any(kw in career_lower for kw in ['electrical engineer']):
            return ["Electrical"]

        if any(kw in career_lower for kw in ['aerospace engineer']):
            return ["Aerospace", "Mechanical", "Civil"]

        if any(kw in career_lower for kw in ['chemical engineer']):
            return ["Chemical"]

        if any(kw in career_lower for kw in ['electronics', 'network engineer', 'cybersecurity', 'cloud engineer']):
            return ["Electronics", "CS", "IT", "Electrical"]

        if any(kw in career_lower for kw in ['architect']):
            return ["Architecture", "Civil"]

        if 'engineer' in career_lower:
            return ["CS", "IT", "Mechanical", "Civil", "Electrical", "Electronics"]

        if any(kw in career_lower for kw in ['doctor', 'surgeon', 'physician']):
            return ["MBBS", "MD", "MS"]

        if any(kw in career_lower for kw in ['dentist']):
            return ["BDS", "MBBS"]

        if any(kw in career_lower for kw in ['nurs']):
            return ["BSc Nursing", "Nursing"]

        if any(kw in career_lower for kw in ['pharmacist', 'pharmaceutical']):
            return ["BPharm", "Pharmacy", "BSc Nursing"]

        if any(kw in career_lower for kw in ['biotechnolog', 'biomedic', 'bioinformatic']):
            return ["BSc Biotechnology", "Biotechnology", "BSc Microbiology", "BSc Biology"]

        if any(kw in career_lower for kw in ['account', 'chartered accountant', 'ca ']):
            return ["BCom", "BAF", "BBA", "Commerce"]

        if any(kw in career_lower for kw in ['financ', 'investment', 'stock', 'actuar', 'bank']):
            return ["BBA Finance", "BCom", "BFM", "BAF", "BBA", "BA Economics", "BSc Mathematics"]

        if any(kw in career_lower for kw in ['business', 'manag', 'entrepreneur', 'market', 'hr', 'retail']):
            return ["BBA", "BMS", "BCom", "MBA"]

        if any(kw in career_lower for kw in ['economist', 'economics']):
            return ["BA Economics", "BSc Economics", "BCom", "BBA"]

        if any(kw in career_lower for kw in ['psycholog']):
            return ["BA Psychology", "BSc Psychology", "Psychology"]

        if any(kw in career_lower for kw in ['journalist', 'media', 'content creator', 'public relation']):
            return ["BA Mass Communication", "BA Journalism", "BA Media", "BA English"]

        if any(kw in career_lower for kw in ['lawyer', 'law', 'legal']):
            return ["BA Political Science", "BA History", "BA Economics", "BA English"]

        if any(kw in career_lower for kw in ['teacher', 'educat']):
            return ["BA Education", "BA", "BSc", "BCom"]

        if any(kw in career_lower for kw in ['sociolog', 'social work', 'anthropolog']):
            return ["BA Sociology", "BA Social Work", "BA History"]

        if any(kw in career_lower for kw in ['designer', 'artist', 'fashion', 'music', 'film']):
            return ["BA", "BFA", "Design", "Arts"]

        if any(kw in career_lower for kw in ['historian', 'political', 'philosopher', 'linguist', 'archaeolog', 'librar']):
            return ["BA History", "BA Political Science", "BA Economics", "BA Philosophy", "BA"]

        if any(kw in career_lower for kw in ['scientist', 'researcher', 'research']):
            return ["BSc Physics", "BSc Chemistry", "BSc Mathematics", "BSc Computer Science", "BSc Biotechnology"]

        if any(kw in career_lower for kw in ['physics']):
            return ["BSc Physics"]

        if any(kw in career_lower for kw in ['chemistry']):
            return ["BSc Chemistry"]

        if any(kw in career_lower for kw in ['mathematics', 'statistician']):
            return ["BSc Mathematics", "BSc Statistics", "Mathematics"]

        # Generic fallback
        return ["BSc", "BCom", "BA", "BBA", "Engineering"]


def is_stream_match(college, target_stream):
    """
    Strictly matches a college to the required stream using the 'streams' array.
    Falls back to 'type' string for backward compatibility.
    """
    if target_stream == "Any":
        return True

    # Use new 'streams' list field for strict matching
    college_streams = [s.lower() for s in college.get('streams', [])]
    if college_streams:
        return target_stream.lower() in college_streams

    # Fallback: use 'type' field string
    college_type = college.get('type', '').lower()
    return target_stream.lower() in college_type


def get_recommended_institutions(predicted_career, standard, city=None, limit=5):
    """
    Core logic to filter and rank colleges based on career profile.
    Strictly matches colleges to the predicted career's required stream and courses.
    Used by both API routes and PDF report generator.
    """
    target_stream = determine_stream(predicted_career)
    required_keywords = get_required_course_keywords(predicted_career, standard)

    # For 10th standard → map to the correct junior college stream
    effective_stream = target_stream
    if standard == "10th":
        if target_stream in ["Engineering", "Medical", "Science"]:
            effective_stream = "Science"
        elif target_stream == "Any":
            # 'Arts/Humanities Stream' predicted career → map to Arts
            career_lower_check = predicted_career.lower()
            if any(kw in career_lower_check for kw in ['art', 'humanit', 'psycholog', 'law', 'writ', 'social', 'media', 'design']):
                effective_stream = "Arts"
        # Commerce and Arts stay as-is

    colleges = load_colleges()

    # Filter by City if provided
    if city:
        colleges = [c for c in colleges if c.get('city', '').lower() == city.lower()]

    matching_colleges = []
    partial_match_colleges = []

    for college in colleges:
        c_standards = college.get('for_standard', [])

        # Skip colleges not for this standard
        if standard not in c_standards:
            continue

        # Strict stream match
        if not is_stream_match(college, effective_stream):
            continue

        available_courses = college.get('courses', [])
        c_copy = dict(college)

        # Find matched courses strictly from required keywords
        matched_courses = [
            course for course in available_courses
            if any(kw.lower() in course.lower() for kw in required_keywords)
        ]

        if standard == "10th":
            if matched_courses:
                c_copy['recommended_path'] = f"Higher Secondary (11th & 12th) - {predicted_career}"
                c_copy['matched_courses'] = matched_courses
                matching_colleges.append(c_copy)
            else:
                # College is right stream but no specific matched course (unlikely with new data)
                if available_courses:
                    c_copy['recommended_path'] = f"Higher Secondary (11th & 12th) - {predicted_career}"
                    c_copy['matched_courses'] = [available_courses[0]]
                    partial_match_colleges.append(c_copy)
        else:
            if matched_courses:
                c_copy['recommended_path'] = f"Undergraduate Degree for {predicted_career}"
                c_copy['matched_courses'] = matched_courses
                matching_colleges.append(c_copy)
            else:
                # Stream matches but no specific course keyword matched
                if available_courses:
                    c_copy['recommended_path'] = f"Undergraduate Degree for {predicted_career}"
                    c_copy['matched_courses'] = [available_courses[0]]
                    partial_match_colleges.append(c_copy)

    # Sort by ranking within each group
    matching_colleges.sort(key=lambda x: x.get('ranking', 999))
    partial_match_colleges.sort(key=lambda x: x.get('ranking', 999))

    # Strict matches first, then partial matches
    results = matching_colleges + partial_match_colleges
    return results[:limit]
