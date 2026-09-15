"""
LLM Integration Service for CogniStudy AI.
Handles API communication with Google Gemini, prompt orchestration,
JSON parsing guardrails, and deterministic offline simulation fallback.
"""
import re
import json
import logging
from typing import Dict, Any, Tuple, Optional
import google.generativeai as genai
from backend import config
from backend import prompts

logger = logging.getLogger("cogni_study.llm")
logging.basicConfig(level=logging.INFO)


def clean_and_parse_json(raw_text: str) -> Dict[str, Any]:
    """
    Cleans LLM response text and extracts valid JSON, stripping markdown fences
    and trailing artifacts if present.
    """
    text = raw_text.strip()
    
    # Check for markdown code blocks
    if "```" in text:
        # Pattern to capture ```json ... ``` or ``` ... ```
        pattern = r"```(?:json)?\s*([\s\S]*?)\s*```"
        match = re.search(pattern, text, re.DOTALL | re.IGNORECASE)
        if match:
            text = match.group(1).strip()
    
    # Attempt standard parse
    try:
        return json.loads(text)
    except json.JSONDecodeError:
        # Secondary fallback: find the first { and last }
        first_brace = text.find("{")
        last_brace = text.rfind("}")
        if first_brace != -1 and last_brace != -1 and last_brace > first_brace:
            extracted = text[first_brace:last_brace + 1]
            return json.loads(extracted)
        raise


def call_gemini(prompt: str, api_key: str, model_name: str = None) -> str:
    """
    Executes a prompt against the Google Gemini API with system instructions.
    """
    active_key = api_key or config.GEMINI_API_KEY
    if not active_key:
        raise ValueError("No Gemini API key configured.")

    active_model = model_name or config.DEFAULT_GEMINI_MODEL
    
    genai.configure(api_key=active_key)
    
    # Try gemini-1.5-flash, fallback to gemini-pro if model not found
    try:
        model = genai.GenerativeModel(
            model_name=active_model,
            system_instruction=prompts.SYSTEM_PROMPT_ACADEMIC_TUTOR
        )
        response = model.generate_content(
            prompt,
            generation_config={"temperature": 0.2, "top_p": 0.95}
        )
        return response.text
    except Exception as e:
        # If model name failed, try alternate common model name
        if "not found" in str(e).lower() and active_model != "gemini-pro":
            logger.warning(f"Model {active_model} not found, retrying with gemini-pro...")
            model = genai.GenerativeModel(model_name="gemini-pro")
            response = model.generate_content(prompt)
            return response.text
        raise e


# ---------------------------------------------------------------------------
# Dynamic Offline Simulation Engine (Defensive Engineering)
# ---------------------------------------------------------------------------

def _extract_key_sentences_and_words(content: str):
    """Extracts non-trivial words and sentences from user content for dynamic simulation."""
    sentences = [s.strip() for s in re.split(r'[.\n]+', content) if len(s.strip()) > 15]
    words = [w.strip(".,;:!?()[]\"'") for w in content.split() if len(w) > 4 and w.isalpha()]
    # Deduplicate while preserving order
    seen = set()
    unique_words = []
    for w in words:
        wl = w.lower()
        if wl not in seen and wl not in {"which", "their", "there", "about", "would", "these", "other"}:
            seen.add(wl)
            unique_words.append(w.capitalize())
    return sentences, unique_words[:10]


def offline_simulate_summary(content: str, style: str, focus_topic: str = None) -> Dict[str, Any]:
    sentences, keywords = _extract_key_sentences_and_words(content)
    lead_topic = focus_topic or (keywords[0] if keywords else "Core Subject")
    
    cues = [
        f"Mechanisms of {lead_topic}",
        f"Key Factors & Variables",
        f"Systemic Implications",
        f"Theoretical Foundations"
    ]
    if len(keywords) >= 3:
        cues[1] = f"Role of {keywords[1]}"
        cues[2] = f"{keywords[2]} Relationships"

    summary_paragraphs = []
    if sentences:
        summary_paragraphs.append(f"**Primary Focus:** {sentences[0]}.")
    if len(sentences) > 1:
        summary_paragraphs.append(f"**Key Findings:** {sentences[1]}.")
    if len(sentences) > 2:
        summary_paragraphs.append(f"**Core Dynamic:** {sentences[2]}.")
    if not summary_paragraphs:
        summary_paragraphs.append(f"Comprehensive analysis of {lead_topic} based on the submitted lecture materials.")

    return {
        "title": f"Synthesis & Cornell Review: {lead_topic}",
        "style": style,
        "cues_and_keywords": cues,
        "notes_summary": "\n\n".join(summary_paragraphs),
        "core_takeaways": [
            f"Central principle focuses on {lead_topic} interactions and governing constraints.",
            f"Key distinction lies between operational inputs and systematic outcomes.",
            f"Essential for examination: Understand causal pathways rather than memorizing isolated facts."
        ],
        "study_questions": [
            f"How does {lead_topic} directly influence the primary equilibrium of the system?",
            f"What would occur if the foundational assumptions in these notes were inverted?",
            f"Can you explain the three-step sequence of this process to a peer without referencing notes?"
        ],
        "action_items": [
            f"Complete 2 active-recall retrieval practice cycles for {lead_topic}.",
            "Map dependencies onto a quick concept diagram before the next seminar."
        ]
    }


def offline_simulate_quiz(content: str, num_questions: int, difficulty: str, question_type: str) -> Dict[str, Any]:
    sentences, keywords = _extract_key_sentences_and_words(content)
    topic = keywords[0] if keywords else "Academic Notes"
    kw1 = keywords[1] if len(keywords) > 1 else "Primary Variable"
    kw2 = keywords[2] if len(keywords) > 2 else "Secondary Component"
    kw3 = keywords[3] if len(keywords) > 3 else "Governing Principle"

    pool = [
        {
            "id": 1,
            "type": "mcq",
            "question": f"Which of the following best characterizes the primary function of {topic} in the context provided?",
            "options": [
                f"A) Acts as the primary catalyst governing {kw1}",
                f"B) Completely eliminates the need for {kw2}",
                f"C) Functions solely as a secondary passive byproduct",
                f"D) Inhibits all downstream regulatory activity"
            ],
            "correct_answer": f"A) Acts as the primary catalyst governing {kw1}",
            "explanation": f"According to the notes, {topic} plays a pivotal role in driving and regulating {kw1}, whereas options B, C, and D misrepresent the mechanism.",
            "hint": f"Think about how {topic} influences energy or information flow."
        },
        {
            "id": 2,
            "type": "mcq" if question_type != "flashcard" else "flashcard",
            "question": f"In what way does {kw1} correlate with changes in {kw2}?",
            "options": [
                f"A) An inverse relationship where increases in {kw1} modulate {kw2}",
                f"B) There is zero observable correlation",
                f"C) A static one-to-one linear dependency",
                f"D) Exponential decay under all normal operating conditions"
            ],
            "correct_answer": f"A) An inverse relationship where increases in {kw1} modulate {kw2}",
            "explanation": f"The dynamic relationship between {kw1} and {kw2} relies on negative feedback or regulatory moderation to maintain stability.",
            "hint": "Consider the stabilizing feedback loops discussed in the text."
        },
        {
            "id": 3,
            "type": "flashcard" if question_type != "mcq" else "mcq",
            "question": f"Define {kw3} and state its primary significance.",
            "options": [
                f"A) The fundamental governing benchmark for system equilibrium",
                f"B) A transient noise parameter ignored in experimental setups",
                f"C) A historical concept that is no longer accepted",
                f"D) A parameter that only applies in isolated vacuum states"
            ] if question_type == "mcq" else None,
            "correct_answer": f"{kw3} provides the boundary condition and foundational metric needed to evaluate overall performance and validity.",
            "explanation": f"Mastery of {kw3} is essential for solving higher-order application problems on this topic.",
            "hint": "Focus on the foundational constraints outlined in your lecture material."
        },
        {
            "id": 4,
            "type": "mcq",
            "question": f"What is the most frequent misconception students encounter regarding {topic}?",
            "options": [
                f"A) Confusing correlation with causation between {topic} and {kw2}",
                f"B) Assuming that {topic} has no mathematical representation",
                f"C) Believing that {topic} was discovered in the 17th century",
                f"D) Treating {topic} as entirely identical to {kw3}"
            ],
            "correct_answer": f"A) Confusing correlation with causation between {topic} and {kw2}",
            "explanation": f"Students often mistakenly deduce that changes in {topic} directly force changes in {kw2} without accounting for intermediate variables.",
            "hint": "Look for confusion between direct drivers and secondary effects."
        }
    ]

    selected = pool[:num_questions]
    return {
        "title": f"Active Recall Mastery Quiz: {topic}",
        "difficulty": difficulty,
        "questions": selected
    }


def offline_simulate_polish(question: str, student_draft: str, target_level: str) -> Dict[str, Any]:
    word_count = len(student_draft.split())
    base_score = min(8, max(5, 5 + (word_count // 30)))
    
    return {
        "original_score": base_score,
        "rubric_evaluation": {
            "conceptual_accuracy": "The draft demonstrates core conceptual understanding but leaves key terminology underspecified.",
            "structure_flow": "The ideas are presented chronologically but lack strong transitional connectors and topic signposting.",
            "academic_tone": "The language leans slightly conversational; replacing informal phrasing with domain-specific terminology will strengthen authority.",
            "evidence_reasoning": "Mechanisms are asserted rather than rigorously demonstrated through causal reasoning."
        },
        "strengths": [
            "Clearly captures the primary question intent and main intuition.",
            "Identifies relevant mechanisms without veering off-topic."
        ],
        "weaknesses": [
            "Uses colloquial phrasing where precise academic terminology is required.",
            "Lacks an explicit thesis-driven opening sentence and conclusive synthesis."
        ],
        "polished_version": (
            f"In addressing the inquiry regarding '{question.strip()}', a rigorous academic analysis requires "
            f"evaluating both the foundational mechanisms and systemic outcomes. {student_draft.strip()} "
            f"Furthermore, this phenomenon must be interpreted through the governing theoretical framework, "
            f"demonstrating that empirical observations align with theoretical predictions and confirming "
            f"that downstream variables remain bounded within expected analytical constraints."
        ),
        "key_improvements_made": [
            "Introduced academic thesis framing to immediately anchor the response.",
            "Replaced informal descriptors with rigorous domain-specific vocabulary.",
            "Reinforced causal coherence between premises and conclusions for examination grading."
        ]
    }


def offline_simulate_explain(concept: str, cognitive_level: str, subject_domain: str = None) -> Dict[str, Any]:
    domain = subject_domain or "General Science & Engineering"
    
    if cognitive_level == "eli5":
        analogy = f"Imagine {concept} is like a busy postal sorting facility: incoming letters must be sorted into bins before the mail trucks can leave, preventing traffic jams."
        explanation = f"At its simplest level, {concept} is all about managing flow and rules. Instead of everything happening all at once in chaos, {concept} acts as the organized traffic controller that makes sure each step happens in the right order."
    elif cognitive_level == "deep_dive":
        analogy = f"In formal mathematical modeling, {concept} mirrors a constrained optimization landscape where boundary parameters dictate stability manifolds."
        explanation = f"From first principles within {domain}, {concept} represents an invariant relationship governed by conservation laws and thermodynamic/computational constraints. When inputs undergo transformation, the systemic equilibrium shifts according to the differential sensitivity of each state variable."
    else: # high_yield_exam
        analogy = f"Think of {concept} as a master thermostat: when system conditions drift outside target bounds, {concept} engages compensatory feedback loops to restore equilibrium."
        explanation = f"{concept} is a foundational principle in {domain}. For examination purposes, focus on the three-phase cycle: (1) Initial trigger conditions, (2) Intermediate state transformation, and (3) Resulting terminal equilibrium. Examiners frequently test the rate-limiting factors that bottleneck this transition."

    return {
        "concept": concept,
        "level": cognitive_level,
        "core_explanation": explanation,
        "intuitive_analogy": analogy,
        "common_misconceptions": [
            f"Assuming {concept} operates instantaneously without propagation latency or transition states.",
            f"Conflating the overarching mechanism of {concept} with its secondary symptoms."
        ],
        "memory_hook_or_mnemonic": f"Remember 'P-A-C-E': Purpose, Activation condition, Causal chain, Equilibrium result.",
        "self_test_challenge": f"If the primary input variable to {concept} was doubled while all other environmental constraints stayed constant, how would the terminal state respond?"
    }


# ---------------------------------------------------------------------------
# High-Level Service Methods with Automatic Fallback
# ---------------------------------------------------------------------------

async def generate_summary(content: str, style: str, focus_topic: str = None, api_key: str = None) -> Tuple[Dict[str, Any], bool, Optional[str]]:
    prompt = prompts.build_cornell_summary_prompt(content, style, focus_topic)
    key = api_key or config.GEMINI_API_KEY

    if key:
        try:
            logger.info("Calling Gemini API for Cornell Summary...")
            raw_response = call_gemini(prompt, api_key=key)
            parsed = clean_and_parse_json(raw_response)
            return parsed, False, None
        except Exception as e:
            logger.error(f"Gemini API error in summarize: {e}. Falling back to simulation engine.")
            simulated = offline_simulate_summary(content, style, focus_topic)
            return simulated, True, f"Live API Notice: {str(e)[:180]}... (Served via Intelligent Offline Engine)"
    else:
        logger.info("No API key provided. Using Intelligent Offline Simulation Engine.")
        simulated = offline_simulate_summary(content, style, focus_topic)
        return simulated, True, "Demo Mode: No API key detected. Generated via Intelligent Academic Simulation Engine."


async def generate_quiz(content: str, num_questions: int, difficulty: str, question_type: str, api_key: str = None) -> Tuple[Dict[str, Any], bool, Optional[str]]:
    prompt = prompts.build_quiz_prompt(content, num_questions, difficulty, question_type)
    key = api_key or config.GEMINI_API_KEY

    if key:
        try:
            logger.info("Calling Gemini API for Quiz Generation...")
            raw_response = call_gemini(prompt, api_key=key)
            parsed = clean_and_parse_json(raw_response)
            return parsed, False, None
        except Exception as e:
            logger.error(f"Gemini API error in quiz: {e}. Falling back to simulation engine.")
            simulated = offline_simulate_quiz(content, num_questions, difficulty, question_type)
            return simulated, True, f"Live API Notice: {str(e)[:180]}... (Served via Intelligent Offline Engine)"
    else:
        logger.info("No API key provided. Using Intelligent Offline Simulation Engine.")
        simulated = offline_simulate_quiz(content, num_questions, difficulty, question_type)
        return simulated, True, "Demo Mode: No API key detected. Generated via Intelligent Academic Simulation Engine."


async def polish_answer(question: str, student_draft: str, target_level: str, api_key: str = None) -> Tuple[Dict[str, Any], bool, Optional[str]]:
    prompt = prompts.build_answer_polish_prompt(question, student_draft, target_level)
    key = api_key or config.GEMINI_API_KEY

    if key:
        try:
            logger.info("Calling Gemini API for Answer Polishing...")
            raw_response = call_gemini(prompt, api_key=key)
            parsed = clean_and_parse_json(raw_response)
            return parsed, False, None
        except Exception as e:
            logger.error(f"Gemini API error in polish: {e}. Falling back to simulation engine.")
            simulated = offline_simulate_polish(question, student_draft, target_level)
            return simulated, True, f"Live API Notice: {str(e)[:180]}... (Served via Intelligent Offline Engine)"
    else:
        logger.info("No API key provided. Using Intelligent Offline Simulation Engine.")
        simulated = offline_simulate_polish(question, student_draft, target_level)
        return simulated, True, "Demo Mode: No API key detected. Generated via Intelligent Academic Simulation Engine."


async def explain_concept(concept: str, cognitive_level: str, subject_domain: str = None, api_key: str = None) -> Tuple[Dict[str, Any], bool, Optional[str]]:
    prompt = prompts.build_feynman_explain_prompt(concept, cognitive_level, subject_domain)
    key = api_key or config.GEMINI_API_KEY

    if key:
        try:
            logger.info("Calling Gemini API for Concept Explanation...")
            raw_response = call_gemini(prompt, api_key=key)
            parsed = clean_and_parse_json(raw_response)
            return parsed, False, None
        except Exception as e:
            logger.error(f"Gemini API error in explain: {e}. Falling back to simulation engine.")
            simulated = offline_simulate_explain(concept, cognitive_level, subject_domain)
            return simulated, True, f"Live API Notice: {str(e)[:180]}... (Served via Intelligent Offline Engine)"
    else:
        logger.info("No API key provided. Using Intelligent Offline Simulation Engine.")
        simulated = offline_simulate_explain(concept, cognitive_level, subject_domain)
        return simulated, True, "Demo Mode: No API key detected. Generated via Intelligent Academic Simulation Engine."
