import re
from typing import Optional

# Comprehensive regex to detect phone numbers in various formats:
# - International: +91-9876543210, +1 234 567 8901, 00919876543210
# - With separators: 987-654-3210, 987.654.3210, 987 654 3210
# - Plain sequences: 9876543210, 09876543210
# - Written out: nine eight seven six five four three two one zero
# - Mixed: 98seven6543210
# Catches numbers with 7+ consecutive digits (after removing separators)

# Regex pattern for numeric phone numbers (7+ digits, with optional country code, separators)
PHONE_REGEX = re.compile(
    r'(?:(?:\+|00)\d{1,3}[-.\s]?)?'   # optional intl prefix like +91, +1, 0091
    r'(?:0\d{1,4}[-.\s]?)?'             # optional trunk prefix like 0, 044
    r'(?:\d[-.\s]?){7,13}\d',           # 7-14 digit number with optional separators
    re.IGNORECASE
)

# Word representations of digits
DIGIT_WORDS = {
    'zero': '0', 'one': '1', 'two': '2', 'three': '3', 'four': '4',
    'five': '5', 'six': '6', 'seven': '7', 'eight': '8', 'nine': '9',
    'oh': '0', 'o': '0',
}

# Pattern for digit words (to catch "nine eight seven six...")
DIGIT_WORD_PATTERN = re.compile(
    r'(?:(?:' + '|'.join(DIGIT_WORDS.keys()) + r')\s*){7,}',
    re.IGNORECASE
)

# Pattern for mixed digit+word sequences like "98seven6five43210"
MIXED_DIGIT_WORD_PATTERN = re.compile(
    r'(?:(?:\d|' + '|'.join(DIGIT_WORDS.keys()) + r')[-.\s]*){7,}',
    re.IGNORECASE
)


def contains_phone_number(text: Optional[str]) -> bool:
    """Check if the given text contains a phone number in any format."""
    if not text:
        return False
    
    # Check for numeric phone patterns
    if PHONE_REGEX.search(text):
        return True
    
    # Check for digit words ("nine eight seven...")
    if DIGIT_WORD_PATTERN.search(text):
        return True
    
    # Check for mixed patterns ("9eight7six...")
    match = MIXED_DIGIT_WORD_PATTERN.search(text)
    if match:
        # Convert matched text to digits and verify it's 7+ digits
        matched_text = match.group(0).lower()
        digits = ''
        i = 0
        while i < len(matched_text):
            if matched_text[i].isdigit():
                digits += matched_text[i]
                i += 1
            elif matched_text[i] in ' -.\t':
                i += 1
            else:
                # Try to match a word
                found_word = False
                for word, digit in DIGIT_WORDS.items():
                    if matched_text[i:].startswith(word):
                        digits += digit
                        i += len(word)
                        found_word = True
                        break
                if not found_word:
                    i += 1
        if len(digits) >= 7:
            return True
    
    return False


def strip_phone_numbers(text: Optional[str]) -> Optional[str]:
    """Remove all phone numbers from the given text, replacing them with '[number removed]'."""
    if not text:
        return text
    
    result = text
    
    # Replace numeric phone patterns
    result = PHONE_REGEX.sub('[number removed]', result)
    
    # Replace digit word patterns
    result = DIGIT_WORD_PATTERN.sub('[number removed]', result)
    
    # Replace mixed patterns (only if they resolve to 7+ digits)
    def replace_mixed(match):
        matched_text = match.group(0).lower()
        digits = ''
        i = 0
        while i < len(matched_text):
            if matched_text[i].isdigit():
                digits += matched_text[i]
                i += 1
            elif matched_text[i] in ' -.\t':
                i += 1
            else:
                found_word = False
                for word, digit in DIGIT_WORDS.items():
                    if matched_text[i:].startswith(word):
                        digits += digit
                        i += len(word)
                        found_word = True
                        break
                if not found_word:
                    i += 1
        if len(digits) >= 7:
            return '[number removed]'
        return match.group(0)
    
    result = MIXED_DIGIT_WORD_PATTERN.sub(replace_mixed, result)
    
    return result
