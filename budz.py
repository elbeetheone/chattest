import streamlit as st
import difflib
from english_words import get_english_words_set
import gensim.downloader
from gensim.utils import simple_preprocess
import nltk
from nltk.corpus import stopwords
import json
import requests
import inflect
import random
from reportlab.lib.pagesizes import A4
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.platypus import Paragraph, SimpleDocTemplate, Spacer
from PyPDF2 import PdfReader, PdfWriter, PageObject
from io import BytesIO
import base64
from openai import OpenAI
import language_tool_python
from textstat import flesch_kincaid_grade
import spacy

engine = inflect.engine()


@st.cache_resource
def load_all_nlp_resources():
    """Load all NLP resources once and cache them"""
    # Download stopwords if needed
    nltk.download('stopwords', quiet=True)
    stop_words = set(stopwords.words('english'))

    # Load word vectors
    wv = gensim.downloader.load("glove-wiki-gigaword-50")

    # Load grammar checker
    grammar_tool = language_tool_python.LanguageTool('en-US')

    # Load spaCy model (download if not present)
    try:
        nlp = spacy.load('en_core_web_sm')
    except OSError:
        import subprocess
        subprocess.run(['python', '-m', 'spacy', 'download', 'en_core_web_sm'])
        nlp = spacy.load('en_core_web_sm')

    return wv, stop_words, grammar_tool, nlp

# Load once at the start
wv, stop_words, grammar_tool, nlp = load_all_nlp_resources()



# Extract parameters with default values if they don't exist
user_words = st.query_params.get("user_words", ["default_value"])
user = st.query_params.get("user", ["default_value"])
foo = st.query_params.get("foo", ["default_value"])
bar = st.query_params.get("bar", ["default_value"])
route = st.query_params.get("route", ["default_value"])


def get_adverb(word):
    # Basic rule to convert adjective to adverb
    if word.endswith('y'):
        return word[:-1] + 'ily'
    elif word.endswith('le'):
        return word[:-1] + 'y'
    elif word.endswith('ic'):
        return word + 'ally'
    else:
        return word + 'ly'

def seenonim(user_response):
    today = foo.split(',')
    nu_list = []
    for num in range(5):
        try:
            response_lower = user_response[num].lower()
            if today[num] == response_lower or  user_response[num] == '_':
                nu_list.append(json.dumps(str(0)))
            elif engine.plural(today[num]) == response_lower or  today[num] == engine.plural(response_lower):
                #control for plurals
                nu_list.append(json.dumps(str(0)))
            elif today[num] == get_adverb(response_lower) or get_adverb(today[num]) == response_lower:
                nu_list.append(json.dumps(str(0)))
                #control for adverbs
            elif difflib.SequenceMatcher(None, today[num], response_lower).ratio() > 0.9:
                nu_list.append(json.dumps(str(0.05)))
                #control for words that are too similarly spelt
            else:
                score = wv.similarity(today[num],response_lower)
                nu_list.append(json.dumps(str((score))))
        except Exception as e:
            # nu_list.append({'word':today[num], 'score': 0, 'scores': 0, 'synonym': user_response[num]})
            nu_list.append(json.dumps(str(0)))
    return nu_list

def get_transcript(topic, transcript, controls):
    topic = simple_preprocess(topic)
    transcript = simple_preprocess(transcript)
    topic = [w for w in topic if w not in stop_words]
    transcript = [w for w in transcript if w not in stop_words]
    min_ratio = 0.5
    if len(transcript) < min_ratio * len(topic):
        similarity = 0.5
        return similarity-controls  # Too short to compare meaningfully
    try:
        distance = wv.wmdistance(topic,transcript)
        similarity = 1 / (1 + distance)  # Invert and normalize (0 to 1 range)
    except:
        similarity = 0.5  # Default if computation fails

    if len(transcript) < min_ratio * len(topic):
        return similarity-controls-0.25  # Too short to compare meaningfully
    else:
        return similarity-controls


def kaawe(topic, transcript):
    # Original preprocessing for WMDistance
    topic_processed = simple_preprocess(topic)
    transcript_processed = simple_preprocess(transcript)
    topic_processed = [w for w in topic_processed if w not in stop_words]
    transcript_processed = [w for w in transcript_processed if w not in stop_words]

    min_ratio = 0.20  # More lenient for kids (was 0.25)

    # 1. WMDistance Score (semantic similarity - did they understand?)
    try:
        distance = wv.wmdistance(topic_processed, transcript_processed)
        wmd_score = 1 / (1 + distance)
    except:
        wmd_score = 0.5

    # Length penalty - more forgiving
    if len(transcript_processed) < min_ratio * len(topic_processed):
        wmd_score -= 0.15  # Smaller penalty (was 0.25)

    # 2. Grammar Score - Focus on major errors only
    grammar_errors = grammar_tool.check(transcript)

    # Filter to only critical errors (ignore minor style suggestions)
    critical_errors = [
        err for err in grammar_errors
        if err.category in ['GRAMMAR', 'TYPOS', 'CONFUSED_WORDS']
        and 'style' not in err.message.lower()
    ]

    word_count = len(transcript.split())
    if word_count > 0:
        # More forgiving: 20+ critical errors per 100 words = 0 score
        error_density = len(critical_errors) / word_count * 100
        grammar_score = max(0, 1 - (error_density / 20))
    else:
        grammar_score = 0

    # 3. Age-Appropriate Readability
    try:
        # Flesch-Kincaid Grade Level - appropriate for kids
        grade_level = flesch_kincaid_grade(transcript)

        # For kids, we want simpler language (grades 3-8 is good)
        # Score higher for age-appropriate complexity
        if 2 <= grade_level <= 8:
            readability_score = 1.0  # Perfect range
        elif grade_level < 2:
            readability_score = 0.8  # Too simple (may be incomplete)
        elif grade_level <= 10:
            readability_score = 0.9  # Slightly advanced but good
        else:
            readability_score = max(0.5, 1 - ((grade_level - 10) * 0.05))
    except:
        readability_score = 0.7  # Neutral default

    # 4. Basic Sentence Completeness (simplified for kids)
    doc = nlp(transcript)
    sentences = list(doc.sents)

    if len(sentences) > 0:
        complete_sentences = 0
        for sent in sentences:
            # More lenient - just needs a verb OR reasonable length
            has_verb = any(token.pos_ in ['VERB', 'AUX'] for token in sent)
            reasonable_length = len(sent) >= 3  # At least 3 words

            if has_verb or reasonable_length:
                complete_sentences += 1

        structure_score = complete_sentences / len(sentences)
    else:
        structure_score = 0

    # 5. Effort/Completeness bonus
    # Reward kids for trying and writing more
    effort_bonus = 0
    if word_count >= 10:  # Wrote at least 10 words
        effort_bonus = 0.05
    if word_count >= 25:  # Wrote a good amount
        effort_bonus = 0.10

    # Combine scores with kid-friendly weights
    weights = {
        'semantic': 0.45,      # Understanding is most important
        'grammar': 0.20,       # Grammar matters but not too harsh
        'readability': 0.15,   # Age-appropriate language
        'structure': 0.20      # Complete thoughts
    }

    final_score = (
        wmd_score * weights['semantic'] +
        grammar_score * weights['grammar'] +
        readability_score * weights['readability'] +
        structure_score * weights['structure'] +
        effort_bonus
    )

    # Cap at 1.0
    final_score = min(1.0, final_score)

    return final_score


def words_web():
    words = list(wv.key_to_index.keys())
    web2lowerset = get_english_words_set(['web2'], lower=True)
    return words, web2lowerset

def paste_budz():
    words, web2lowerset = words_web()
    def has_more_than_five_similars(word, web2lowerset, wv):
        similar_words = [similar_word[0] for similar_word in wv.most_similar(word, topn=10)]
        return len([sw for sw in similar_words if sw in web2lowerset]) > 5

    # Filter words by length and presence in web2lowerset
    ran_letter = [num for num in words if len(num) >= 5 and num in web2lowerset]

    # Ensure today_words has 5 words that meet the condition
    today_words = []
    while len(today_words) < 5:
        candidate = random.choice(ran_letter)  # Choose a random word from ran_letter
        # Add the candidate if it meets the condition and isn't already in today_words
        if has_more_than_five_similars(candidate, web2lowerset, wv) and candidate not in today_words:
            today_words.append(candidate)
    return today_words


def get_feedback(content, content_str):
    packet = BytesIO()
    doc = SimpleDocTemplate(packet, pagesize=A4)
    styles = getSampleStyleSheet()

    # **Custom Styles**
    header_style = ParagraphStyle('Header', parent=styles['Heading1'], fontSize=16, textColor=colors.black, spaceAfter=8, bold=True)
    subheader_style = ParagraphStyle('SubHeader', parent=styles['Heading2'], fontSize=12, textColor=colors.black, spaceAfter=5, bold=True)
    bullet_style_1 = ParagraphStyle('Bullet', parent=styles['Normal'], bulletText='', textColor=colors.green, spaceAfter=5, leftIndent=20)
    bullet_style_2 = ParagraphStyle('Bullet', parent=styles['Normal'], bulletText='', textColor=colors.red, spaceAfter=5, leftIndent=20)
    star_style = ParagraphStyle('Stars', parent=styles['Normal'], fontSize=12, textColor=colors.orange, spaceAfter=5)
    body_style = ParagraphStyle('Body', parent=styles['Normal'], textColor=colors.black, spaceAfter=8, bold=False)
    final_style = ParagraphStyle('Header', parent=styles['Heading1'], fontSize=16, textColor=colors.black, spaceAfter=8, bold=True)


    lines = content_str.split("\n")
    for num in lines:
        if '#HEADER#' in num:
            content.append(Paragraph(f"<b>{num.strip('#HEADER#')}</b>", header_style))
        if '#SUBHEADER#' in num and 'Question' in num:
            content.append(Paragraph("<b>_________________________________</b>", subheader_style))
        if '#SUBHEADER#' in num:
            content.append(Paragraph(f"<b>{num.strip('#SUBHEADER#')}</b>", subheader_style))
        if '#BULLET#' in num and '+' in num:
            content.append(Paragraph(f"{num.strip('#BULLET#')}", bullet_style_1))
        if '#BULLET#' in num and '-' in num:
            content.append(Paragraph(f"{num.strip('#BULLET#')}", bullet_style_2))
        if '#STARS#' in num:
            content.append(Paragraph(f"<b>{num.strip('#STARS#')}</b>", star_style))
        if '#BODY#' in num:
            content.append(Paragraph(f"{num.strip('#BODY#')}", body_style))
        if '#FINAL#' in num:
            content.append(Paragraph("<b>_________________________________</b>"))
            content.append(Paragraph("<b>*     *     *</b>", final_style))
            content.append(Paragraph(f"<b>{num.strip('#FINAL#')}</b>", final_style))
        else:
            pass

    return content, packet, doc


def overlay_evaluation_on_existing_pdf(existing_pdf_path, nu_str):
    # Step 1: Read the existing PDF
    existing_pdf = PdfReader(existing_pdf_path)
    output = PdfWriter()


    content = get_feedback([], nu_str)
    doc = content[-1]
    doc.build(content[0])
    packet = content[1]
    packet.seek(0)

    # Step 3: Merge new content onto existing PDF
    new_pdf = PdfReader(packet)
    cover_pdf = PdfReader('cover_page_aceit.pdf')

    # Add cover pages first
    for page in cover_pdf.pages:
        output.add_page(page)

    for i in range(len(existing_pdf.pages)):
        page = existing_pdf.pages[i]

        if i == 0:
            continue

        new_blank_page = PageObject.create_blank_page(width=page.mediabox[2], height=page.mediabox[3])
        new_blank_page.merge_page(existing_pdf.pages[0])
        new_blank_page.merge_page(page)
        output.add_page(new_blank_page)

    for j in range(len(new_pdf.pages)):
        new_page = new_pdf.pages[j]
        new_blank_page = PageObject.create_blank_page(width=new_page.mediabox[2], height=new_page.mediabox[3])
        new_blank_page.merge_page(existing_pdf.pages[0])
        new_blank_page.merge_page(new_page)
        output.add_page(new_blank_page)

    pdf_buffer = BytesIO()
    output.write(pdf_buffer)
    pdf_buffer.seek(0)

    encoded_pdf = base64.b64encode(pdf_buffer.read()).decode("utf-8")

    url = st.secrets['WEB_4']
    requests.post(url, json={'pdf': encoded_pdf, 'user': user})


if bar == st.secrets['BAR_1']:
    user_words_ = user_words.split(',')
    url = st.secrets['WEB']
    myobj = {'today_words': seenonim(user_words_), 'user':user, 'foo':foo, 'user_words': user_words, 'route': route}
    requests.post(url, json = myobj)



if bar == st.secrets['BAR_2']:
    url = st.secrets['WEB_2']
    foo = foo.replace(',',' ').lower()
    user_words_ = user_words.split(',')
    controls = (user_words_.count('um') + user_words_.count('uh')) * 0.25
    user_words = user_words.replace(',',' ').lower()
    myobj = {'score': get_transcript(user_words, foo, controls), 'user':user}
    requests.post(url, json = myobj)


if bar == st.secrets['BAR_3']: #wordbudz league
    foo_ = int(foo) if foo.isdigit() else None
    list_to_pass = []
    for num in range(foo_):
        list_to_pass.append(paste_budz())
    url = st.secrets['WEB_3']
    myobj = {'user_words': list_to_pass, 'league': route}
    requests.post(url, json = myobj)

if bar == st.secrets['BAR_4']: #ace_it
    user_response = requests.get(st.secrets['WEB_5']+user).json()
    client = OpenAI(api_key=st.secrets['open_ai_key'])
    response = client.chat.completions.create(
    model="gpt-4o-mini",
    messages=[
        {"role": "system", "content": st.secrets['PROMPT']},
        {"role": "user", "content": f'{user_response} \n' + st.secrets['PROMPT_1']}
        ])

    content = response.choices[0].message.content
    # myobj = {'content': content}
    # requests.post('https://mealy-expensive-bone.anvil.app/_/api/log_resp', json = myobj)
    # Might need somewhere to log the responses
    overlay_evaluation_on_existing_pdf('watermark_aceit.pdf', content)
    #for pdf creation

if bar == st.secrets['BAR_5']: # kaawe
    class_ = foo
    user = user
    myobj = {'user':user, 'class_':class_}
    passage = requests.get('https://svelte-possible-work.anvil.app/_/api/get_passages', json=myobj)
    passage = passage.json()
    comp_score = kaawe(passage[0], passage[-1])
    url = st.secrets['WEB_6']
    myobj = {'user':user, 'class_':class_, 'score': comp_score}
    requests.post(url, json = myobj)

    #use api to get user's summary and og passage
