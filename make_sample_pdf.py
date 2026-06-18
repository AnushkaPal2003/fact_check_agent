from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer
from reportlab.lib.styles import getSampleStyleSheet

doc = SimpleDocTemplate("/home/claude/fact-check-agent/sample_trap_document.pdf", pagesize=letter)
styles = getSampleStyleSheet()
story = []

title = "Acme AI Corp — Company Overview"
story.append(Paragraph(title, styles["Title"]))
story.append(Spacer(1, 12))

paragraphs = [
    "Acme AI Corp was founded in 2015 and has quickly become a leader in enterprise software.",
    "As of 2024, OpenAI's ChatGPT has over 800 million weekly active users worldwide.",
    "The Eiffel Tower, completed in 1989, remains one of the most visited landmarks in the world.",
    "Apple's market capitalization crossed $1 trillion for the first time in 2010.",
    "Our flagship product is used by more than 50,000 companies across 30 countries.",
    "The world's population reached 8 billion people in November 2022.",
    "Acme AI Corp raised $120 million in Series C funding led by fictional investors in 2023.",
    "Tesla delivered approximately 1.8 million vehicles globally in 2023.",
]

for p in paragraphs:
    story.append(Paragraph(p, styles["BodyText"]))
    story.append(Spacer(1, 8))

doc.build(story)
print("PDF created.")