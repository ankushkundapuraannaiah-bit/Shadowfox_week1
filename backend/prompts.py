"""
Prompt engineering templates for CogniStudy AI.
Defines system instructions, few-shot prompt architectures, and structured schemas.
"""
from typing import Dict, Any


SYSTEM_PROMPT_ACADEMIC_TUTOR = """You are CogniStudy AI, an elite academic learning specialist and cognitive science tutor.
Your mission is to help students learn faster, retain information deeper, and achieve academic mastery through structured pedagogical frameworks.

Core Directives:
1. Always adhere strictly to the requested format (valid JSON only, no markdown enclosing fences unless specifically asked).
2. Avoid generic conversational fluff (never say "Sure! Here is...", "As an AI...", "I hope this helps!").
3. Apply active recall, Bloom's Taxonomy, and the Feynman technique.
4. Keep explanations crystal clear, scientifically accurate, and high-yield.
"""


def build_cornell_summary_prompt(content: str, style: str, focus_topic: str = None) -> str:
    focus_clause = f"Focus particularly on aspects related to: '{focus_topic}'." if focus_topic else ""
    
    return f"""Task: Transform the provided lecture/study notes into a structured pedagogical summary following the Cornell Notes framework.
{focus_clause}

Input Notes:
\"\"\"
{content}
\"\"\"

Format Requirement:
Return ONLY a valid JSON object matching this schema exactly:
{{
  "title": "A concise, academic topic title",
  "style": "{style}",
  "cues_and_keywords": ["Keyword/Cue 1", "Keyword/Cue 2", "Keyword/Cue 3", "Keyword/Cue 4"],
  "notes_summary": "A detailed, well-structured synthesis of the main concepts using markdown formatting (bolding, subheadings, bullet points where appropriate).",
  "core_takeaways": ["High-yield takeaway 1", "High-yield takeaway 2", "High-yield takeaway 3"],
  "study_questions": ["Self-testing question 1?", "Self-testing question 2?", "Self-testing question 3?"],
  "action_items": ["Actionable next step or topic to review 1", "Actionable next step 2"]
}}

Respond with raw JSON only. Do not enclose in backticks or markdown fences.
"""


def build_quiz_prompt(content: str, num_questions: int, difficulty: str, question_type: str) -> str:
    return f"""Task: Generate an active-recall self-assessment quiz based strictly on the provided study notes.
Target difficulty: {difficulty.upper()}
Number of questions: {num_questions}
Question format: {question_type.upper()} (if 'mcq', generate multiple choice with 4 distinct options; if 'flashcard', provide question and concise answer card; if 'mixed', alternate).

Input Study Notes:
\"\"\"
{content}
\"\"\"

Format Requirement:
Return ONLY a valid JSON object matching this schema:
{{
  "title": "Topic Quiz Title",
  "difficulty": "{difficulty}",
  "questions": [
    {{
      "id": 1,
      "type": "mcq",
      "question": "Clear, challenging question testing understanding rather than rote recall?",
      "options": ["A) Option 1", "B) Option 2", "C) Option 3", "D) Option 4"],
      "correct_answer": "B) Option 2",
      "explanation": "Detailed explanation of why this answer is correct and why common misconceptions are wrong.",
      "hint": "Subtle clue directing thought process without giving the answer away."
    }}
  ]
}}

Ensure distractors in MCQs are plausible misconceptions.
Respond with raw JSON only. Do not enclose in backticks or markdown fences.
"""


def build_answer_polish_prompt(question: str, student_draft: str, target_level: str) -> str:
    return f"""Task: As an academic examiner at the {target_level.upper()} level, evaluate the student's draft answer and rewrite it into an exemplary high-scoring submission.

Exam / Assignment Question:
\"\"\"
{question}
\"\"\"

Student's Draft Answer:
\"\"\"
{student_draft}
\"\"\"

Evaluation Rubric:
1. Conceptual Accuracy & Depth
2. Structure & Logical Flow
3. Academic Tone & Vocabulary
4. Evidence / Justification

Format Requirement:
Return ONLY a valid JSON object matching this schema:
{{
  "original_score": 6,
  "rubric_evaluation": {{
    "conceptual_accuracy": "Feedback on correctness and depth",
    "structure_flow": "Feedback on organizational clarity",
    "academic_tone": "Feedback on register and diction",
    "evidence_reasoning": "Feedback on examples and reasoning"
  }},
  "strengths": ["Clear strength 1", "Clear strength 2"],
  "weaknesses": ["Weakness or omission 1", "Weakness or omission 2"],
  "polished_version": "A complete, publication-grade, high-scoring model answer that maintains the student's original core ideas while dramatically enhancing rigor, clarity, and articulation.",
  "key_improvements_made": ["Specific improvement 1", "Specific improvement 2", "Specific improvement 3"]
}}

Respond with raw JSON only. Do not enclose in backticks or markdown fences.
"""


def build_feynman_explain_prompt(concept: str, cognitive_level: str, subject_domain: str = None) -> str:
    domain_clause = f"in the context of {subject_domain}" if subject_domain else ""
    
    level_descriptions = {
        "eli5": "Explain using intuitive everyday metaphors, zero jargon, and vivid analogies suitable for anyone (Feynman Technique).",
        "high_yield_exam": "Explain with structured clarity, high-yield definitions, mechanisms, and key formulas or relationships needed for exams.",
        "deep_dive": "Provide an undergraduate-level rigorous breakdown from first principles, theoretical underpinnings, and boundary conditions."
    }
    
    guideline = level_descriptions.get(cognitive_level, level_descriptions["high_yield_exam"])

    return f"""Task: Explain the academic concept '{concept}' {domain_clause}.
Cognitive Depth Level: {cognitive_level.upper()} ({guideline})

Format Requirement:
Return ONLY a valid JSON object matching this schema:
{{
  "concept": "{concept}",
  "level": "{cognitive_level}",
  "core_explanation": "Thorough, engaging explanation tailored to the requested depth level.",
  "intuitive_analogy": "A memorable real-world analogy illuminating the core mechanism.",
  "common_misconceptions": ["Frequent mistake or misconception students make 1", "Misconception 2"],
  "memory_hook_or_mnemonic": "A clever mnemonic, acronym, or memory anchor to remember this effortlessly.",
  "self_test_challenge": "A quick thought-experiment or mini-challenge question for the student to verify their understanding."
}}

Respond with raw JSON only. Do not enclose in backticks or markdown fences.
"""
