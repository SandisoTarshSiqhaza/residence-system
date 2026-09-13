from difflib import SequenceMatcher

SIMILARITY_THRESHOLD = 0.5


def find_possible_duplicate(new_description, existing_requests):
    """
    Compares a new request description against a list of (description, category_id)
    tuples for currently-open requests in the same room.

    Returns (matched_description, similarity_score) for the closest match if it's
    above SIMILARITY_THRESHOLD, otherwise None.

    Uses difflib's SequenceMatcher, which needs no extra install (unlike scikit-learn's
    TF-IDF/cosine-similarity approach) -- good enough for catching near-duplicate
    phrasing like "leaking tap" vs "tap is leaking again".
    """
    best_score = 0.0
    best_match = None

    new_text = new_description.strip().lower()
    if not new_text:
        return None

    for existing_text, _category_id in existing_requests:
        score = SequenceMatcher(None, new_text, existing_text.strip().lower()).ratio()
        if score > best_score:
            best_score = score
            best_match = existing_text

    if best_match and best_score >= SIMILARITY_THRESHOLD:
        return (best_match, best_score)
    return None
