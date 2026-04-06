import re
import nltk
from nltk.corpus import stopwords
from nltk.stem import WordNetLemmatizer
import pandas as pd

# Downloading NLTK data 
try:
    nltk.data.find('tokenizers/punkt')  # Fixed: 'tokenizers' not 'tokenizer'
except LookupError:
    nltk.download('punkt')
    nltk.download('stopwords')
    nltk.download('wordnet')
    nltk.download('omw-1.4')

class TextPreprocessor:
    def __init__(self):
        self.stop_words = set(stopwords.words('english'))  # Fixed: changed to stop_words
        self.lemmatizer = WordNetLemmatizer()

        # Custom Stopwords:
        self.custom_stopwords = {'br', 'html', 'href', 'http', 'www', 
                                 'com', 'org', 'net', 'would', 'could', 
                                 'get', 'one', 'also', 'even', 'product'}
        self.stop_words.update(self.custom_stopwords)  # Fixed: changed to stop_words

    def preprocess(self, text):
        if pd.isna(text) or not isinstance(text, str):
            return ""
        
        text = text.lower()

        # Fixed HTML tag regex (added closing '>' and made it non-greedy)
        text = re.sub(r'<.*?>', '', text)

        # Remove URLs
        text = re.sub(r'http\S+|www\S+|https\S+', '', text)

        # Keep only letters and spaces
        text = re.sub(r'[^a-zA-Z\s]', '', text)

        # Remove extra spaces
        text = re.sub(r'\s+', ' ', text).strip()

        words = text.split()
        # Fixed: changed to self.stop_words
        words = [self.lemmatizer.lemmatize(w) for w in words if w not in self.stop_words and len(w) > 2]

        return " ".join(words)
    
# Creating Global Instance
preprocessor = TextPreprocessor()