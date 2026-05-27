import yaml

# Base dictionary for 500+ items
new_grammar = {}

roles = [
    "Software Engineer", "Data Scientist", "Product Manager", "UI/UX Designer",
    "DevOps Engineer", "Cybersecurity Expert", "Database Administrator", "Cloud Architect",
    "Machine Learning Engineer", "Frontend Developer", "Backend Developer", "Full Stack Developer",
    "Mobile App Developer", "Game Developer", "QA Automation Engineer", "Systems Analyst",
    "Copywriter", "Digital Marketer", "SEO Specialist", "Content Strategist",
    "Social Media Manager", "Brand Strategist", "Public Relations Specialist", "Email Marketer",
    "Growth Hacker", "Technical Writer", "Grant Writer", "Speechwriter",
    "Financial Analyst", "Investment Banker", "Accountant", "Economist",
    "Venture Capitalist", "Risk Manager", "Actuary", "Management Consultant",
    "HR Manager", "Recruiter", "Operations Manager", "Supply Chain Analyst",
    "Project Manager", "Agile Coach", "Scrum Master", "Business Analyst",
    "Lawyer", "Paralegal", "Compliance Officer", "Intellectual Property Attorney",
    "Doctor", "Nurse", "Pharmacist", "Medical Researcher",
    "Teacher", "Professor", "Instructional Designer", "Academic Researcher"
] # 56 roles

for i, role in enumerate(roles):
    new_grammar[f"ROLE_{i}"] = f"Act as a world-class {role} with over 15 years of industry experience and deep subject matter expertise. Think step-by-step and provide authoritative, well-reasoned answers."
    new_grammar[f"ROLE_C_{i}"] = f"Take on the persona of an expert {role}. Provide clear, concise, and highly technical insights without any unnecessary introductory fluff."
    new_grammar[f"ROLE_M_{i}"] = f"You are a mentor and senior {role}. Guide me through the problem using Socratic questioning, best practices, and real-world examples."

tones = [
    "Professional", "Casual", "Humorous", "Sarcastic", "Empathetic",
    "Authoritative", "Persuasive", "Inspirational", "Academic", "Journalistic",
    "Witty", "Direct", "Polite", "Aggressive", "Passionate",
    "Formal", "Informal", "Objective", "Subjective", "Conversational",
    "Didactic", "Inquisitive", "Reflective", "Satirical", "Cynical",
    "Optimistic", "Pessimistic", "Pragmatic", "Idealistic", "Stoic",
    "Enthusiastic", "Melancholic", "Nostalgic", "Whimsical", "Reverent"
] # 35 tones

for i, tone in enumerate(tones):
    new_grammar[f"TONE_{i}"] = f"Adopt a {tone} tone for the duration of this response. Use appropriate vocabulary, sentence structure, and phrasing that reflect this specific style."
    new_grammar[f"TONE_W_{i}"] = f"Write the following content strictly using a {tone} voice. Ensure the mood is consistent throughout the entire text and avoids conflicting emotions."
    new_grammar[f"TONE_A_{i}"] = f"Adjust your communication style to be highly {tone}. Tailor your words to resonate with an audience that expects this exact type of delivery."

formats = [
    "JSON", "XML", "CSV", "Markdown", "HTML", "CSS", "YAML", "TOML",
    "SQL", "Bash", "Python", "JavaScript", "TypeScript", "C++", "Java",
    "C#", "Go", "Rust", "Swift", "Kotlin", "PHP", "Ruby", "Perl",
    "Haskell", "Scala", "Lua", "Dart", "R", "MATLAB", "Objective-C",
    "Bullet points", "Numbered list", "Table", "Flowchart", "Mind map",
    "Essay", "Poem", "Haiku", "Sonnet", "Limerick", "Screenplay", "Play",
    "Novel", "Short story", "Fable", "Myth", "Legend", "Fairy tale",
    "Biography", "Autobiography", "Memoir", "Diary", "Journal", "Letter"
] # 54 formats

for i, fmt in enumerate(formats):
    new_grammar[f"FMT_{i}"] = f"Format the output strictly as valid {fmt}. Do not include any conversational filler, introductory remarks, or markdown wrappers like backticks unless required by the format."
    new_grammar[f"FMT_C_{i}"] = f"Convert the provided information into a clean, well-structured {fmt} representation. Ensure all syntax is correct and ready for immediate use."
    new_grammar[f"FMT_O_{i}"] = f"Your final deliverable must be exclusively in {fmt}. Any text outside of the requested format will be considered a failure."

constraints = [
    "under 50 words", "under 100 words", "under 200 words", "under 500 words",
    "exactly 3 sentences", "exactly 5 paragraphs", "no more than 1 page",
    "using simple English", "without any jargon", "using complex vocabulary",
    "with citations", "without citing sources", "in a step-by-step guide",
    "with pros and cons", "using a SWOT analysis", "using a PESTLE analysis",
    "using the STAR method", "using the SMART criteria", "with an executive summary",
    "with a clear call to action", "without using the word 'delve'",
    "without using the phrase 'in conclusion'", "avoiding passive voice",
    "using active voice", "with a high readability score", "optimized for SEO",
    "with emojis", "without any emojis", "using bullet points for lists",
    "highlighting key terms in bold", "italicizing quotes", "with a table of contents"
] # 32 constraints

for i, const in enumerate(constraints):
    new_grammar[f"CONST_{i}"] = f"Ensure the final output is strictly {const}. Pay close attention to this constraint and revise your answer before finalizing it to guarantee compliance."
    new_grammar[f"CONST_A_{i}"] = f"It is absolutely critical that the response is {const}. Any deviation from this rule will render the output unusable."
    new_grammar[f"CONST_B_{i}"] = f"Double-check your work to ensure it is {const}. If it is not, iteratively refine the text until it perfectly matches the requirement."

import sys
try:
    with open("prompt-smuggler/.smugglerrc.yaml", "r", encoding="utf-8") as f:
        config = yaml.safe_load(f)
except FileNotFoundError:
    config = {"grammar": {}}

if not config:
    config = {}
if "grammar" not in config:
    config["grammar"] = {}

config["grammar"].update(new_grammar)

with open("prompt-smuggler/.smugglerrc.yaml", "w", encoding="utf-8") as f:
    yaml.dump(config, f, allow_unicode=True, sort_keys=False)

print(f"Added {len(new_grammar)} items. Total grammar size: {len(config['grammar'])}")
