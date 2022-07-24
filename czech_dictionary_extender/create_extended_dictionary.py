import urllib.request
import os
from pyglossary import Glossary
import wordfreq
from czech_inflections_lemmatizer.lemmatizer import Lemmatizer
def download_GNU_dictionary():
    """Downloads the dictionary from https://www.svobodneslovniky.cz/data/en-cs.txt"""

    if not os.path.isfile('en-cs.txt'):
        urllib.request.urlretrieve('https://www.svobodneslovniky.cz/data/en-cs.txt', 'en-cs.txt')
    else:
        print('File already exists')        

def create_extended_dictionary():
    """Creates the extended dictionary"""

    download_GNU_dictionary()

    with open('en-cs.txt', 'r', encoding="utf-8") as f:
        lines = f.readlines()

    # Create an empty dictionary to store all english words for each czech word
    dictionary = {}

    with open('czech-english-dict.txt', 'w', encoding="utf-8") as f:
        for line in lines:
            if line.startswith('#'):
                continue
            else:
                # Load the TSV line
                line = line.split('\t')
                # Get the czech word
                czech_word = line[1]
                if czech_word == None or czech_word == "":
                    continue
                # Get the english word
                english_word = line[0]
                # Add the english word to the dictionary
                if czech_word in dictionary:
                    dictionary[czech_word].append(english_word)
                else:
                    dictionary[czech_word] = [english_word]

        lem = Lemmatizer("C:/Users/hanne/Documents/Programme/czech-inflections-lemmatizer/lemma_inflection.db")
        # Iterate through the dictionary and write the words to the file
        for czech_word in dictionary:
            # Get the english words
            english_words = dictionary[czech_word]
            # If czech word ends with " se", remove the " se"
            if czech_word.endswith(" se"):
                czech_word_for_inflection_search = czech_word[:-3]
            else:
                czech_word_for_inflection_search = czech_word

            # Iterate through the english words and calculate the frequency of each word
            czech_inflections = lem.find_inflections(czech_word_for_inflection_search)
            #Remove duplicates and czech_word from czech inflections
            czech_inflections = list(set(czech_inflections + [czech_word_for_inflection_search]) - {czech_word})
            
            # Append the czech inflections to the czech word, everything separated by |
            if len(czech_inflections) > 0:
                czech_word += '|' + '|'.join(czech_inflections)
            sorted_words = sorted(english_words, key=lambda x: wordfreq.word_frequency(x, "cs"), reverse=True)
            # Write the czech word and the english words (separated by comma) to the file
            f.write(czech_word + '\t' + ', '.join(sorted_words) + '\n')

def create_stardict_dict():
    Glossary.init()
    glos = Glossary()
    glos.convert(inputFilename="czech-english-dict.txt", inputFormat="Tabfile", outputFilename="czech-english-dict.ifo", outputFormat="Stardict")

if __name__ == "__main__":
    create_extended_dictionary()
    create_stardict_dict()
    