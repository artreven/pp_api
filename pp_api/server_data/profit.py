server = 'http://profit.poolparty.biz'
profit_pid = '1DE00088-2B4C-0001-9BB3-1C5234FF8640'
virtuoso_sparql_endpoint = 'https://profit-virtuoso.poolparty.biz/sparql'
ld_graphs = {
    'http://www.telegraph.co.uk/business/rss.xml': ['text', 'title', 'title'],
    'http://feeds.bbci.co.uk/news/business/your_money/rss.xml': ['text', 'title', 'title'],
    'https://content.guardianapis.com/money': ['body', 'headline', 'trail-text'],
    'https://content.guardianapis.com/business': ['body', 'headline', 'trail-text'],
    'http://rssfeeds.usatoday.com/usatodaycommoney-topstories&x=1': ['text', 'title', 'title'],
    'https://us.spindices.com/rss': ['text', 'title', 'title'],
    'http://www.ecb.europa.eu/home/html/rss': ['text', 'title', 'title'],
    'http://www.washingtonpost.com/news/get-there/feed/': ['text', 'title', 'title'],  # any texts???
    'http://rss.cnn.com/rss/money_pf': ['text', 'title', 'title'],
    'http://rss.cnn.com/rss/money_autos': ['text', 'title', 'title'],
    'http://rss.cnn.com/rss/money_funds': ['text', 'title', 'title'],
    'http://rss.cnn.com/rss/money_pf_college': ['text', 'title', 'title'],
    'http://rss.cnn.com/rss/money_pf_insurance': ['text', 'title', 'title'],
    'http://rss.cnn.com/rss/money_pf_taxes': ['text', 'title', 'title'],
    'http://rss.cnn.com/rss/money_retirement': ['text', 'title', 'title'],
    'http://www.dailymail.co.uk/money/index.html': ['text', 'title', 'title'],
    'http://www.dailymail.co.uk/money/markets/index.html': ['text', 'title', 'title'],
    'http://www.dailymail.co.uk/money/saving/index.html': ['text', 'title', 'title'],
    'http://www.dailymail.co.uk/money/investing/index.html': ['text', 'title', 'title'],
    'http://www.dailymail.co.uk/money/cars/index.html': ['text', 'title', 'title'],
    'http://www.dailymail.co.uk/money/holidays/index.html': ['text', 'title', 'title'],
    'http://www.dailymail.co.uk/money/cardsloans/index.html': ['text', 'title', 'title'],
    'http://www.dailymail.co.uk/money/pensions/index.html': ['text', 'title', 'title'],
    'http://www.dailymail.co.uk/money/mortgageshome/index.html': ['text', 'title', 'title'],
    'http://www.dailymail.co.uk/money/experts/index.html': ['text', 'title', 'title'],
    'http://www.dailymail.co.uk/money/investingshow/index.html': ['text', 'title', 'title'],
    'http://www.nytimes.com/services/xml/rss/nyt/YourMoney.xml': ['text', 'title', 'title'],
    'http://europa.eu/newsroom/rss-feeds': ['text', 'title', 'title']
}
test_server = 'https://pp-profit-dev.semantic-web.at'
test_pid = '1DF17390-6A1A-0001-BCC7-ED9C1680AE80'
gs_profit_space = "d8b07c03-153d-405c-99f2-ae67a1eee438"
