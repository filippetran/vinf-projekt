import re
from nltk import word_tokenize
from nltk.corpus import stopwords
from datetime import datetime as dt
import emoji


def parse_abstracts(xml_file, page_abstracts: list, page_id: int, index: dict):
    for line in xml_file:

        # if len(page_abstracts) == 4:
        #     break

        if "<page>" in line:
            page_title = ""
            page_abstract = ""

            while True:
                
                page_line = next(xml_file)
                #print("PL: ", page_line)
                if "<title>" in page_line:
                    #print(page_line)
                    page_title = re.search("(?<=<title>)(.*)(?=<\/title>)", page_line).group(0)
                    
                    continue

                if "<text" in page_line:
                    #print(page_line)
                    text_size = int(re.search("(?<=bytes=\")(.*)(?=\" )", page_line).group(0))
                    
                    # check if wiki page contains text
                    if text_size>300:
                        
                        while True:
                            check_line = next(xml_file)

                            # the '==' marks the title of another section (after abstract)
                            if "==" in check_line:
                                break
                            
                            # first line
                            if "'''" in check_line:
                                page_abstract += check_line

                                #average length of abstract is 200 words, average english word has 4.7 ~ 5 characters
                                while(len(page_abstract) < 1000):
                                    page_abstract += next(xml_file)
                                break

                        page_abstract = re.sub("{{.*?}}|\[\[|\]\]", "", page_abstract)

                        page_abstract = re.sub("&quot;", "\"", page_abstract)
                        page_abstract = re.sub("&lt;.*?&gt;", "", page_abstract)
                        page_abstract = re.sub("\n", " ", page_abstract)


                        page_abstract = re.sub('\|', ' ', page_abstract)
                        page_abstract = re.sub('[^A-Za-z0-9\-\. ]+', '', page_abstract)

                        
                        page_abstracts.append(page_abstract)
                        
                        index_abstract(page_abstract, index, page_id)
                        page_id += 1
                    
                if "</page>" in page_line:
                    break


# adds given abstract to index
def index_abstract(abstract: str, index: dict, page_id: int):
    tokens = word_tokenize(abstract)
    english_stopwords = set(stopwords.words('english'))


    tokens_without_stopwords = []
    for token in tokens:
        if token.lower() not in english_stopwords:
            tokens_without_stopwords.append(token)

    for token in tokens_without_stopwords:
        if token not in index.keys():
            index[token] = [{
                'page_id': page_id,
                'freq': abstract.count(token)
            }]
        else:
            index[token].append(
                {
                    'page_id': page_id,
                    'freq': abstract.count(token)
                }
            )


def keyFunc(obj: object):
    return obj['score']

def main():

    print("Parsing started: " + str(dt.now()) + "\n")
    xml_file = open('data/enwiki-latest-pages-articles1.xml-p1p41242', 'r', encoding='utf-8')

    page_abstracts = []
    page_id = 0
    inverted_index = dict()

    parse_abstracts(xml_file, page_abstracts, page_id, inverted_index)

    print("Finished parsing: " + str(dt.now()))


    max_results = 4
    print("\n---------------------------------------------------")
    print("Search something (enter 'q' to quit)")
    print("---------------------------------------------------")
    searchicon = str(emoji.emojize(':magnifying_glass_tilted_left:') + " :  ")
    while True:
        query = input(searchicon)

        if query == "q":
            break
        elif len(query) > 0:
            search_results = []
            words = query.split()        
            for word in words:
                if word in inverted_index.keys():
                    for occurrence in inverted_index[word]:

                        new_result = {
                            'text': page_abstracts[occurrence['page_id']],
                            'score': 1
                        }

                        # check if result text is already in search results, increase score if yes
                        flag = True
                        for res in search_results:
                            if new_result['text'] == res['text']:
                                res['score'] = res['score'] + 1
                                flag = False

                        # add new result
                        if flag:
                            search_results.append(new_result)
                                    

            # sort search results by 'score' attribute, descending           
            search_results.sort(key=keyFunc, reverse=True)

            if(len(search_results) == 0):
                print("No results found")
            else:
                c=0
                for res in search_results:
                    c+=1
                    print(res['score'])
                    print(res['text'] + "\n")
                    if c == max_results:
                        break
        else:
            print("Input cannot be empty.")


    xml_file.close()


if __name__ == "__main__":
    main()