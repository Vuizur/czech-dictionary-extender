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
    glos.convert(inputFilename="czech-english-dict.txt", inputFormat="Tabfile", outputFilename="czech-english-dict.ifo", outputFormat="Stardict", infoOverride={"sourceLang": "cs", "targetLang": "en", "name": "Czech-English Dictionary", "author": "Vuizur"})

def add_stardict_files_to_tar_gz():
    """Adds the stardict files to the tar.gz file using python libraries"""

    import tarfile

    # Convert line endings of IFO file to Unix
    with open('czech-english-dict.ifo', 'rb') as f:
        lines = f.readlines()
    with open('czech-english-dict.ifo', 'wb') as f:
        for line in lines:
            f.write(line.replace(b'\r\n', b'\n'))

    # Create the czech-english-dict folder
    if not os.path.isdir('czech-english-dict'):
        os.mkdir('czech-english-dict')

    # Move all files into the folder czech-english-dict using python library
    import shutil
    shutil.move('czech-english-dict.ifo', 'czech-english-dict/czech-english-dict.ifo')
    shutil.move('czech-english-dict.idx', 'czech-english-dict/czech-english-dict.idx')
    shutil.move('czech-english-dict.dict.dz', 'czech-english-dict/czech-english-dict.dict.dz')
    shutil.move('czech-english-dict.syn', 'czech-english-dict/czech-english-dict.syn')

    # Delete tarfile
    if os.path.isfile('czech-english-dict.tar.gz'):
        os.remove('czech-english-dict.tar.gz')
    # Create the tar.gz file
    with tarfile.open("czech-english-dict.tar.gz", "w:gz") as tar:
        # Add the dictionary folder to the tar.gz file
        tar.add('czech-english-dict')

if __name__ == "__main__":
    create_extended_dictionary()
    create_stardict_dict()
    add_stardict_files_to_tar_gz()
    