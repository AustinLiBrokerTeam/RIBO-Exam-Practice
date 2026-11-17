import os
import re
import json

# Files in same folder as script
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))

INPUT_FILE = os.path.join(SCRIPT_DIR, "questions.txt")
OUTPUT_FILE = os.path.join(SCRIPT_DIR, "questions.js")
VIDEO_FILES = [
    "Chapter 1 Introduction To General Insurance.mp4",
    "Chapter 2 How Insurance is Organized in Canada.mp4",
    "Chapter 3 Insurance Contracts and the Role of Government in Insurance.mp4",
    "Chapter 4 The Insurance Buying Process.mp4",
    "Chapter 5 Regulation Of Insurance Contracts.mp4",
    "Chapter 6 The Regulation of Insurance Brokers.mp4",
    "Chapter 7 Property Insurance.mp4",
    "Chapter 8 Liability Insurance.mp4",
    "Chapter 9 Automobile Insurance.mp4",
    "Chapter 10 Commercial Property Insurance.mp4",
    "Chapter 11.mp4",
]

print("Looking for:", INPUT_FILE)

if not os.path.exists(INPUT_FILE):
    print("ERROR: questions.txt not found")
    input("Press Enter to exit...")
    quit()

with open(INPUT_FILE, "r", encoding="utf-8", errors="ignore") as f:
    text = f.read()

print("Characters loaded:", len(text))

if len(text.strip()) == 0:
    print("ERROR: File is empty")
    input("Press Enter to exit...")
    quit()

# Split into lines
lines = [
    line.strip()
    for line in text.splitlines()
    if line.strip()
]

print("Lines found:", len(lines))

chapters = []

for match in re.finditer(
    r"(Chapter\s+\d+)(.*?)(?=Chapter\s+\d+|$)",
    text,
    flags=re.DOTALL | re.IGNORECASE
):

    chapter_title = match.group(1).strip()

    chapter_text = match.group(2)

    chapter_lines = [
        x.strip()
        for x in chapter_text.splitlines()
        if x.strip()
    ]

    questions = []

    i = 0

    while i < len(chapter_lines):


        if (
            i + 5 < len(chapter_lines)
            and re.match(r"^\d+\.$", chapter_lines[i + 5])
        ):

            qid = int(chapter_lines[i + 5][:-1])

            questions.append({
                "id": qid,
                "question": chapter_lines[i + 4],
                "options": [
                    chapter_lines[i],
                    chapter_lines[i + 1],
                    chapter_lines[i + 2],
                    chapter_lines[i + 3]
                ],
                "answer": None,
                "explanation": ""
            })

            i += 6

        else:
            i += 1

    chapter_number = len(chapters) + 1

    chapters.append({
        "id": chapter_number,
        "title": os.path.splitext(VIDEO_FILES[chapter_number - 1])[0] if chapter_number <= len(VIDEO_FILES) else chapter_title,
        "video": f"videos/{VIDEO_FILES[chapter_number - 1]}" if chapter_number <= len(VIDEO_FILES) else "",
        "questions": questions
    })

# Write JS file
with open(OUTPUT_FILE, "w", encoding="utf-8") as f:

    f.write(
        "window.chapters = "
        + json.dumps(chapters, indent=4)
        + ";"
    )

total_questions = sum(
    len(ch["questions"])
    for ch in chapters
)

print()
print("SUCCESS")
print("Chapters:", len(chapters))
print("Questions:", total_questions)
print("Saved to:", OUTPUT_FILE)

input("Press Enter to close...")