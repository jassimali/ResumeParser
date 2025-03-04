import re
import spacy
from pdfminer.high_level import extract_text
from spacy.matcher import Matcher, PhraseMatcher

# Load NLP model
nlp = spacy.load("en_core_web_sm")
matcher = Matcher(nlp.vocab)
phrase_matcher = PhraseMatcher(nlp.vocab, attr="LOWER")  # Case-insensitive matching

# List of technical skills to detect
skill_keywords = [
    "Python", "Java", "C++", "C#", "C", "Figma", "Canva", "Excel", "JavaScript", 
    "TypeScript", "React", "Next.js", "Angular", "Vue.js", "Node.js", "HTML", 
    "CSS", "SQL", "MySQL", "PostgreSQL", "MongoDB", "NoSQL", "Docker", "Kubernetes", 
    "AWS", "Azure", "GCP", "Git", "CI/CD", "Agile", "Scrum", "Linux", "Windows", 
    "DevOps", "Testing", "QA", "REST APIs", "GraphQL", "Machine Learning", "AI", 
    "Data Science", "Cloud Computing", "Cybersecurity", "Networking", 
    "Mobile Development", "Android", "iOS", "UI/UX", "OpenAI", "MS Office"
]

# Convert skill keywords into spaCy patterns
skill_patterns = [nlp(skill) for skill in skill_keywords]
phrase_matcher.add("SKILLS", skill_patterns)

def extract_text_from_pdf(pdf_path):
    """Extract text using pdfminer only."""
    try:
        text = extract_text(pdf_path)
        if text.strip():
            print("\n🔹 Extracted Raw Text:\n", text)  # Print extracted text for debugging
            return text.strip()
    except Exception as e:
        print("Error extracting text from PDF:", e)
    
    return ""

def extract_full_name(nlp_doc):
    """Uses spaCy's Matcher to detect full names (first + last name)."""
    pattern = [{"POS": "PROPN"}, {"POS": "PROPN"}]  # Proper Noun + Proper Noun (e.g., "John Doe")
    
    # Add pattern only once to avoid duplicate rule errors
    if "FULL_NAME" not in matcher:
        matcher.add("FULL_NAME", [pattern])
    
    matches = matcher(nlp_doc)
    for _, start, end in matches:
        span = nlp_doc[start:end]
        return span.text  # Return the first full name found

    return None  # If no match found

def extract_skills(text):
    """Extracts skills from the resume using spaCy PhraseMatcher and regex."""
    doc = nlp(text)
    skills = set()

    # Use PhraseMatcher to find skills in the text
    matches = phrase_matcher(doc)
    for match_id, start, end in matches:
        skills.add(doc[start:end].text)

    # Fallback Regex-Based Skill Extraction (if spaCy misses skills)
    skill_pattern = r"\b(?:{})\b".format("|".join(re.escape(skill) for skill in skill_keywords))
    regex_skills = re.findall(skill_pattern, text, re.IGNORECASE)

    # Combine skills from NER, PhraseMatcher, and regex
    all_skills = list(skills.union(set(regex_skills)))

    print("\n🛠️ Extracted Skills:", all_skills)  # Print extracted skills for debugging
    return all_skills if all_skills else ["Not Found"]

def extract_details(text):
    """Extracts Name, Email, Phone, GitHub, LinkedIn, and Skills from resume text."""
    details = {}
    doc = nlp(text)

    # 🔹 Extract Email
    email_pattern = r"[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}"
    emails = re.findall(email_pattern, text)
    details["email"] = emails[0] if emails else "Not Found"

    # 🔹 Extract Phone Number (Using Regex - spaCy Doesn't Detect Phone Numbers Well)
    phone_pattern = r"\+?\d{1,3}[-.\s]?\(?\d{2,4}\)?[-.\s]?\d{3}[-.\s]?\d{3,4}"
    phones = re.findall(phone_pattern, text)
    details["phone"] = phones[0] if phones else "Not Found"

    # 🔹 Extract GitHub
    github_pattern = r"github\.com/([a-zA-Z0-9-]+)"
    github_matches = re.findall(github_pattern, text)
    details["github"] = f"github.com/{github_matches[0]}" if github_matches else "Not Found"

    # 🔹 Extract LinkedIn
    linkedin_pattern = r"linkedin\.com/in/([a-zA-Z0-9-]+)"
    linkedin_matches = re.findall(linkedin_pattern, text)
    details["linkedin"] = f"linkedin.com/in/{linkedin_matches[0]}" if linkedin_matches else "Not Found"

    # 🔹 Extract Name using Multiple Strategies
    name = extract_full_name(doc)  # Try with Matcher

    # Step 1️⃣: Look for "Name:" pattern in the top 15 lines
    lines = text.split("\n")
    if not name:
        for line in lines[:15]:  
            match = re.search(r"(?i)Name[:\s]*([A-Z][a-z]+(?:\s[A-Z][a-z]+)*)", line)
            if match:
                name = match.group(1)
                break

    # Step 2️⃣: If no name found, check the first significant non-empty line
    if not name:
        for line in lines:
            words = line.strip().split()
            if len(words) == 2 and all(word[0].isupper() for word in words):  # Looks like a name
                name = line.strip()
                break

    # Step 3️⃣: If still no name, use spaCy NLP (Named Entity Recognition)
    if not name:
        for ent in doc.ents:
            if ent.label_ == "PERSON":
                name = ent.text
                break

    details["name"] = name if name else "Not Found"

    # 🔹 Extract Skills using PhraseMatcher + regex
    details["skills"] = extract_skills(text)

    print("\n✅ Extracted Details:\n", details)  # Print extracted details
    return details
