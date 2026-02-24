import pymorphy3


class KeywordPostProccessor:
    def __init__ (self) -> None:
        self.morph = pymorphy3.MorphAnalyzer()

    def process(self, phrases: list[str]) -> list[str]:
        phrases = self.clean_empty(phrases)
        phrases = self.remove_exact_duplicates(phrases)
        phrases = self.remove_morphological_duplicates(phrases)
        phrases = self.remove_nested_phrases(phrases)
        
        return phrases


    def clean_empty(self, phrases: list[str]) -> list[str]:
        return [phrase.strip() for phrase in phrases if phrase.strip()]
    

    def remove_exact_duplicates(self, phrases: list[str]) -> list[str]:
        return list(dict.fromkeys(phrases))
    

    def remove_morphological_duplicates(self, phrases: list[str]) -> list[str]:
        unique_phrases: dict[str, str] = {}

        for phrase in phrases:
            lemma = self.lemmatize(phrase)
            if lemma not in unique_phrases:
                unique_phrases[lemma] = phrase

        return list(unique_phrases.values())


    def remove_nested_phrases(self, phrases: list[str]) -> list[str]:
        lemmas = [self.lemmatize(phrase) for phrase in phrases]
        cleaned_phrases = []

        for i, first_lemma in enumerate(lemmas):
            keep_phrase = True
            for j, second_lemma in enumerate(lemmas):
                if i != j and first_lemma in second_lemma:
                    if len(first_lemma) < len(second_lemma):
                        keep_phrase = False
                        break
            if keep_phrase:
                cleaned_phrases.append(phrases[i])

        return cleaned_phrases


    def lemmatize(self, phrase: str) -> str:
        words = phrase.lower().split()
        lemmas = [self.morph.parse(word)[0].normal_form for word in words]

        return " ".join(lemmas)