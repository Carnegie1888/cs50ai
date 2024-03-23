import os
import random
import re
import sys

DAMPING = 0.85
SAMPLES = 10000


def main():
    if len(sys.argv) != 2:
        sys.exit("Usage: python pagerank.py corpus")
    corpus = crawl(sys.argv[1])
    ranks = sample_pagerank(corpus, DAMPING, SAMPLES)
    print(f"PageRank Results from Sampling (n = {SAMPLES})")
    for page in sorted(ranks):
        print(f"  {page}: {ranks[page]:.4f}")
    ranks = iterate_pagerank(corpus, DAMPING)
    print(f"PageRank Results from Iteration")
    for page in sorted(ranks):
        print(f"  {page}: {ranks[page]:.4f}")


def crawl(directory):
    """
    Parse a directory of HTML pages and check for links to other pages.
    Return a dictionary where each key is a page, and values are
    a list of all other pages in the corpus that are linked to by the page.
    """
    pages = dict()

    # Extract all links from HTML files
    for filename in os.listdir(directory):
        if not filename.endswith(".html"):
            continue
        with open(os.path.join(directory, filename)) as f:
            contents = f.read()
            links = re.findall(r"<a\s+(?:[^>]*?)href=\"([^\"]*)\"", contents)
            pages[filename] = set(links) - {filename}

    # Only include links to other pages in the corpus
    for filename in pages:
        pages[filename] = set(
            link for link in pages[filename]
            if link in pages
        )

    return pages


def transition_model(corpus, page, damping_factor):
    """
    Return a probability distribution over which page to visit next,
    given a current page.

    With probability `damping_factor`, choose a link at random
    linked to by `page`. With probability `1 - damping_factor`, choose
    a link at random chosen from all pages in the corpus.
    """
    distribution = {}
    links = len(corpus[page])

    if links == 0:
        damping_factor = 1
        all = list(corpus.keys())
        num_of_all = len(corpus.values)

        for next in all:
            distribution[next] = damping_factor / num_of_all

        return distribution
    else:
        all = list(corpus.keys())
        num_of_all = len(all)

        for next in all:
            distribution[next] = damping_factor / num_of_all

        for next in corpus[page]:
            distribution[next] += damping_factor / links

        return distribution





def sample_pagerank(corpus, damping_factor, n):
    """
    Return PageRank values for each page by sampling `n` pages
    according to transition model, starting with a page at random.

    Return a dictionary where keys are page names, and values are
    their estimated PageRank value (a value between 0 and 1). All
    PageRank values should sum to 1.
    """
    pr = {}

    pages = list(corpus.keys())

    for page in pages:
        pr[page] = 0

    page = random.choice(pages)
    pr[page] += 1

    for i in range(n):
        dict = transition_model(corpus, page, damping_factor)
        population = list(dict.keys())
        weights = list(dict.values())

        page = random.choices(population, weights, k=1)[0]
        pr[page] += 1

    for page in pr:
        pr[page] = pr[page] / n

    return pr

def iterate_pagerank(corpus, damping_factor):
    """
    Return PageRank values for each page by iteratively updating
    PageRank values until convergence.

    Return a dictionary where keys are page names, and values are
    their estimated PageRank value (a value between 0 and 1). All
    PageRank values should sum to 1.
    """
    pr = {}

    pages = list(corpus.keys())
    all = len(pages)
    init = 1 / all

    for page in pages:
        pr[page] = init

    while True:
        out = True

        for page in pr:
            last = pr[page]
            pr[page] = (1 - damping_factor) / all 
            for parent, pages_set in corpus.items():
                if page in pages_set:
                    pr[page] += damping_factor * pr[parent] / len(pages_set)
            
            if abs(last - pr[page]) > 0.001:
                out = False

        if out:
            return pr

        


    




if __name__ == "__main__":
    main()
