import editdistance
from transformers import BertTokenizer, BertForMaskedLM
import torch
from textblob import TextBlob
import nltk
from nltk.corpus import words

# Downloading vocabulary for word corrections
nltk.download('words')
vocabulary = words.words()

# Load pre-trained BERT tokenizer and model
tokenizer = BertTokenizer.from_pretrained('bert-base-uncased')
model = BertForMaskedLM.from_pretrained('bert-base-uncased')
model.eval()

def generate_candidates(misspelled_word, vocabulary, max_candidates=5):
    # Calculate edit distance and generate candidate words
    candidates = sorted(vocabulary, key=lambda word: editdistance.eval(word, misspelled_word))
    return candidates[:max_candidates]

def rank_candidates(sentence, candidates, target_word):
    scores = []
    masked_sentence = sentence.replace(target_word, '[MASK]', 1)
    input_ids = tokenizer.encode(masked_sentence, return_tensors='pt')
    masked_index = torch.where(input_ids == tokenizer.mask_token_id)[1]

    if masked_index.nelement() == 0:
        # If no masked index found, return the target word
        return target_word

    with torch.no_grad():
        outputs = model(input_ids)
        predictions = outputs[0]

    masked_index = masked_index[0]  # Take the first masked index

    for candidate in candidates:
        candidate_token_id = tokenizer.convert_tokens_to_ids(candidate)
        if candidate_token_id >= predictions.size(-1):
            continue
        candidate_score = predictions[0, masked_index, candidate_token_id].item()
        scores.append((candidate, candidate_score))

    if not scores:
        # If no valid candidates, return the target word as a fallback
        return target_word

    best_candidate = max(scores, key=lambda item: item[1])[0]
    return best_candidate

def correct_spelling_with_textblob(text):
    blob = TextBlob(text)
    corrected_text = blob.correct()
    return str(corrected_text)

def correct_spelling_with_bert(text, vocabulary):
    words_in_text = text.split()
    corrected_words = []

    for word in words_in_text:
        candidates = generate_candidates(word, vocabulary)
        if candidates:
            corrected_word = rank_candidates(text, candidates, word)
            corrected_words.append(corrected_word)
        else:
            corrected_words.append(word)

    corrected_text = ' '.join(corrected_words)
    return corrected_text

# Example usage
text = "I awnt ot eta an aple."
# Initial correction with TextBlob
initial_corrected_text = correct_spelling_with_textblob(text)
print("Initial correction with TextBlob:", initial_corrected_text)

# Further refinement with BERT
final_corrected_text = correct_spelling_with_bert(initial_corrected_text, vocabulary)
print("Final correction with BERT:", final_corrected_text)
