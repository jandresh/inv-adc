from metapub import PubMedFetcher
pmids = [2020202, 1745076, 2768771, 8277124, 4031339]
fetch = PubMedFetcher()
for pmid in pmids:
    article = fetch.article_by_pmid(pmid)
    print(pmid)
    print(article.title)
    print(article.citation)