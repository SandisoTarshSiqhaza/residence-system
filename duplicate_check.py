from difflib import SequenceMatcher

SIMILARITY_TRESHOLD = 0.5

def find_possible_duplicate(new_description, existing_requests):
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
