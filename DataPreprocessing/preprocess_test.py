# Sample list of questions
from DataPreprocessing.data_preprocessing import remove_punctuation, to_lowercase, tokenize_txt, remove_stopwords, \
    apply_stemming, apply_lemmatization

questions = [
    "How old are you!",
    "Email address, please.",
    "Thanks! What's next?",
    "What are the foods that contain the most vitamin C?"

]

# Apply the function to each question in the list
questions_no_punct = [remove_punctuation(question) for question in questions]
questions_lower = [to_lowercase(question) for question in questions_no_punct]
tokenized_questions = tokenize_txt(questions_lower)  # Tokenize once after cleaning
no_stopwords_questions = remove_stopwords(tokenized_questions)  # Remove stopwords from tokenized text
stemmed_questions = apply_stemming(no_stopwords_questions)
lemmatized_questions = apply_lemmatization(stemmed_questions)

# Print the cleaned questions
for question in lemmatized_questions:
    print(question)

