from django.shortcuts import render
import os
from groq import Groq
from pypdf import PdfReader


# Create Groq client using environment variable
client = Groq(
    api_key=os.environ.get("GROQ_API_KEY")
)


def ask_groq(prompt):
    """Send a prompt to Groq and return the AI response."""

    response = client.chat.completions.create(
        model="openai/gpt-oss-120b",
        messages=[
            {
                "role": "user",
                "content": prompt
            }
        ],
        temperature=0.7
    )

    return response.choices[0].message.content


def home(request):

    result = ""

    # Get saved PDF text from session
    pdf_text = request.session.get("pdf_text", "")

    if request.method == "POST":

        action = request.POST.get("action")

        # ==================================================
        # PDF UPLOAD
        # ==================================================

        if action == "pdf_upload":

            uploaded_file = request.FILES.get("pdf_file")

            if uploaded_file:

                if uploaded_file.name.lower().endswith(".pdf"):

                    try:

                        reader = PdfReader(uploaded_file)

                        pages = []

                        for page in reader.pages:

                            text = page.extract_text()

                            if text:
                                pages.append(text)

                        pdf_text = "\n".join(pages)

                        if pdf_text.strip():

                            # Save PDF text in session
                            request.session["pdf_text"] = pdf_text

                            result = (
                                "✅ PDF uploaded successfully!\n\n"
                                "You can now ask questions about this PDF."
                            )

                        else:

                            result = (
                                "⚠️ Could not extract text from this PDF."
                            )

                    except Exception as e:

                        result = (
                            f"❌ Error reading PDF: {str(e)}"
                        )

                else:

                    result = (
                        "⚠️ Please upload a PDF file."
                    )

            else:

                result = (
                    "⚠️ Please select a PDF file."
                )

        # ==================================================
        # ASK QUESTION FROM PDF
        # ==================================================

        elif action == "ask_pdf":

            question = request.POST.get(
                "pdf_question",
                ""
            ).strip()

            pdf_text = request.session.get(
                "pdf_text",
                ""
            )

            if not pdf_text:

                result = (
                    "⚠️ Please upload a PDF first."
                )

            elif not question:

                result = (
                    "⚠️ Please enter a question."
                )

            else:

                # Limit PDF text to avoid very large requests
                context = pdf_text[:12000]

                prompt = f"""
You are an AI Exam Preparation Assistant.

Answer the student's question using ONLY the information
provided in the study material below.

STUDY MATERIAL:
{context}

STUDENT QUESTION:
{question}

Instructions:
- Give a clear and simple answer.
- Use information from the study material.
- Do not use outside information.
- If the answer is not available in the study material,
  say exactly:

"The answer is not available in the uploaded PDF."
"""

                try:

                    result = ask_groq(prompt)

                except Exception as e:

                    result = (
                        f"❌ AI Error: {str(e)}"
                    )

        # ==================================================
        # NORMAL AI FEATURES
        # ==================================================

        else:

            subject = request.POST.get(
                "subject",
                ""
            ).strip()

            topic = request.POST.get(
                "topic",
                ""
            ).strip()

            if subject and topic:

                # ------------------------------------------
                # EXPLAIN
                # ------------------------------------------

                if action == "explain":

                    prompt = f"""
You are an AI Exam Preparation Assistant.

Subject: {subject}
Topic: {topic}

Explain this topic in simple language for a college student.

Include:

1. Definition
2. Main concepts
3. Simple example
4. Important exam points
5. Short summary
"""

                # ------------------------------------------
                # IMPORTANT QUESTIONS
                # ------------------------------------------

                elif action == "questions":

                    prompt = f"""
You are an AI Exam Preparation Assistant.

Subject: {subject}
Topic: {topic}

Generate 5 important exam questions about this topic.

Include:
- 2 mark questions
- 5 mark questions
- 10 mark questions

Do not give answers.
"""

                # ------------------------------------------
                # MCQ
                # ------------------------------------------

                elif action == "mcq":

                    prompt = f"""
You are an AI Exam Preparation Assistant.

Subject: {subject}
Topic: {topic}

Generate 5 multiple-choice questions.

For each question provide:

A) Option
B) Option
C) Option
D) Option

Clearly show:
- Correct answer
- Short explanation
"""

                # ------------------------------------------
                # STUDY PLAN
                # ------------------------------------------

                elif action == "studyplan":

                    prompt = f"""
You are an AI Exam Preparation Assistant.

Subject: {subject}
Topic: {topic}

Create a simple 7-day study plan.

For each day include:

- Topics to study
- Revision
- Practice activity

At the end give one exam preparation tip.
"""

                # ------------------------------------------
                # INVALID ACTION
                # ------------------------------------------

                else:

                    prompt = (
                        "Please select a valid option."
                    )

                # ------------------------------------------
                # CALL GROQ
                # ------------------------------------------

                try:

                    result = ask_groq(prompt)

                except Exception as e:

                    result = (
                        f"❌ AI Error: {str(e)}"
                    )

            else:

                result = (
                    "Please enter both Subject and Topic."
                )

    return render(
        request,
        "index.html",
        {
            "result": result,
            "pdf_text": pdf_text
        }
    )