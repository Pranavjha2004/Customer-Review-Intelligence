import re
import nltk
from nltk.corpus import stopwords
from nltk.stem import WordNetLemmatizer
import pandas as pd


# Downloading NLTK data 

try:
    nltk.data.find('tokenizer/punkt')

except LookupError:
    nltk.download('punkt')
    nltk.download('stopwords')
    nltk.download('wordnet')
    nltk.download('omw-1.4')

class TextPreprocessor:
    def __init__(self):
        self.stopwords = set(stopwords.words('english'))
        self.lemmatizer = WordNetLemmatizer()

        # Custom Stopwords:
        self.custom_stopwords = {'br', 'html', 'href', 'http', 'www', 
                                 'com', 'org', 'net', 'would', 'could', 
                                 'get', 'one', 'also', 'even', 'product'}
        self.stopwords.update(self.custom_stopwords)

    def preprocess(self,text):
        if pd.isna(text) or not isinstance(text, str):
            return ""
        
        text = text.lower()

        text = re.sub(r'<.*?', '', text)

        text = re.sub(r'http\S+|www\S+|https\S+', '', text)

        text = re.sub(r'[^a-zA-Z\s]', '', text)

        text = re.sub(r'\s+', ' ', text).strip()

        words = text.split()
        words = [self.lemmatizer.lemmatize(w) for w in words if w not in self.stop_words and len(w)> 2]

        return " ".join(words)
    
# Creating Global Instance
preprocessor = TextPreprocessor()