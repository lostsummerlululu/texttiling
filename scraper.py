#!/usr/bin/python
"""
Accesses articles through plosOne, cleans html to get the text only.
Also records the number of section breaks and the locations of these
breaks.
"""

from bs4 import BeautifulSoup
from urllib import urlopen
import sys
import string

def get_text(url, outfile): 
    section_breaks = []    
    section_titles = []
    num_paragraphs = 0
    output_text = ""
    html_doc = urlopen(url).read()
    soup = BeautifulSoup(html_doc)

    for section in soup.find_all("div", {"class":"section"}):
        # non-standard section, skip it        
        if section.find("p").get('class') is not None:
            continue
        
        # record the start of a new section
        if(num_paragraphs > 0):
            section_breaks.append(num_paragraphs)
            section_titles.append(section.find("h3").get_text())

        # remove figures, links, other stuff
        for figure in section.find_all("div", {"class":"figure"}):
            figure.extract()
        for link in section.find_all("a"):
            link.extract()

        children = section.findChildren()
        for child in children:
            if child.name != "p" and child.name != "h4":
                child.extract()
        
        children = section.findChildren()
        for child in children:
            if child.name == "p":
                for link in child.find_all("a"):
                    link.extract()
                ptext = filter(lambda x: x in string.printable, child.get_text())
                output_text += ptext + "\n\n"
                num_paragraphs += 1        
            elif child.name == "h4":
                if num_paragraphs != section_breaks[-1]:          
                    section_breaks.append(num_paragraphs)
                    section_titles.append(child.get_text())
                    

    # the page was bad, didn't get the article
    if len(section_breaks) == 0:
        return False

    # create the metadata about breaks    
    metadata = str(len(section_breaks)) + "\n"
    for i in xrange(len(section_breaks)):  
        metadata += str(section_breaks[i]) + "\n"
        #metadata += ": " + section_titles[i] + "\n"

    # write to the output file    
    f = open(outfile, 'w')
    f.write(metadata)
    f.write(output_text)
    f.close()
    return True
    
def main(argv):
    # seed is the starting article id. We will just increment 
    # this id and hope to hit more articles, since they are
    # labelled sequentially.
    seed = "0113812"
    i = 0 
    j = 0
    N = 20
    # we are guaranteed to get N articles.
    while i < N:
        article_id = str(int(seed) + j).zfill(len(seed))
        link = "http://dx.plos.org/10.1371/journal.pone." + article_id
        j += 1
        if get_text(link, "articles/article" + str(i).zfill(3) + ".txt"):
            i += 1

if __name__ == "__main__":
    main(sys.argv)



