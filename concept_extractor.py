import nltk
from nltk.tokenize import word_tokenize
from nltk.corpus import stopwords
from collections import Counter

nltk.download("punkt")
nltk.download("stopwords")

def extract_concepts(text, top_n=8):
    """
    Extract clean, meaningful concepts from lecture text.
    """

    stop_words = set(stopwords.words("english"))

    words = word_tokenize(text.lower())

    # ✅ STRICT filtering
    filtered = [
        w for w in words
        if w.isalpha()
        and w not in stop_words
        and len(w) > 3            # remove short junk
        and w not in {"sorry", "apologies"}
    ]

    freq = Counter(filtered)

    concepts = [w for w, _ in freq.most_common(top_n)]

    # Remove duplicates safely
    concepts = list(dict.fromkeys(concepts))

    return concepts
