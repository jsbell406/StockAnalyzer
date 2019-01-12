# StockAnalyzer

Performs non-technical Stock Analysis, including:

- News Analysis: Aggregates news articles mentioning a given stock and rates them.
- Rating Analysis: Aggregates Stock "Ratings" across a variety of sources, creating an average rating.

## Installation

1. Clone the repo into your desired directory, step into the directory:

```bash
git clone https://github.com/William-Lake/StockAnalyzer.git

cd StockAnalyzer
```

2. (Optional, but *highly recommended*.) create your virtual environment:

NOTE: Conda is not required, but it's what was used when creating this library.

```bash
conda create --name=StockAnalyzer_env python=3
```

3. Install the required libraries:

```bash
pip3 install -r requirements.txt
```

## Usage

There are three separate tools in this repo:

1. StockNewsAnalyzer - Analyzes a Stock's News articles.
2. StockRater - Aggregates ratings of a stock from other rating sites.
3. HistogramGenerator - Generates a histogram for a Stock's News scores.

### StockNewsAnalyzer

```bash
python3 stock_news_analyzer.py NVDA
```

Output:
```
Average Sentiment Score for NVDA: 0.3212948148148148
```

### StockRater

```bash
python3 stock_rater.py NVDA
```

Output:
```
Average Buy/Hold/Sell rating for NVDA: 0
```

### HistogramGenerator

#### One Stock

```bash
python3 histogram_generator.py NVDA
```

![NVDA](images/NVDA_20181215.png)

#### Multiple Stocks

```bash
python3 histogram_generator.py NVDA AMD
```

![NVDA & AMD](images/NVDA_AMD_20181215.png)

## Built With

- [peewee](https://pypi.org/project/peewee/): Peewee is a simple and small ORM. It has few (but expressive) concepts, making it easy to learn and intuitive to use.
    - Also made use of it's [pwiz script](http://docs.peewee-orm.com/en/latest/peewee/playhouse.html#pwiz-a-model-generator) which was incredibly useful.
- [feedparser](https://pypi.org/project/feedparser/): Parse Atom and RSS feeds in Python.
- [nltk](https://pypi.org/project/nltk/): Natural Language Toolkit
- [vaderSentiment](https://pypi.org/project/vaderSentiment/): VADER-Sentiment-Analysis 
- [matplotlib](https://pypi.org/project/matplotlib/): Python plotting package
- [numpy](https://pypi.org/project/numpy/): Aarray processing for numbers, strings, records, and objects.
