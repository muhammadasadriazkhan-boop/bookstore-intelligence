# Bookstore Intelligence - Analysis Results

**Name:** Asad Riaz | **Roll No:** 22i-0651 | **Section:** BSBA - A

Dataset: 60 books scraped from 3 pages of books.toscrape.com (generated automatically by bookstore_scraper.py).

## Mission 4 - Intelligence Analysis

1. **Most expensive book:** Slow States of Collapse: Poems - £57.31 (3 stars)
2. **Cheapest book:** In Her Wake - £12.84 (1 stars)
3. **Average book price:** £35.00
4. **Books with a 5-star rating:** 14
5. **Books in stock:** 100.0%
6. **Top 5 highest-rated books** (all 5 stars; ties broken by lowest price):

   | # | Title | Price | Rating |
   |---|---|---|---|
   | 1 | Sophie's World | £15.94 | 5 |
   | 2 | Thirst | £17.27 | 5 |
   | 3 | Set Me Free | £17.46 | 5 |
   | 4 | The Four Agreements: A Practical Guide to Personal Freedom | £17.66 | 5 |
   | 5 | #HigherSelfie: Wake Up Your Life. Free Your Soul. Find Your Tribe. | £23.11 | 5 |

7. **Cheapest 5-star book:** Sophie's World - £15.94

## Bonus 3 - Books per star rating

| Rating | Books | Average price |
|---|---|---|
| 1 | 15 | £34.31 |
| 2 | 8 | £33.87 |
| 3 | 13 | £38.81 |
| 4 | 10 | £35.53 |
| 5 | 14 | £32.48 |

![Rating counts](rating_counts.png)

## Final Challenge - The CEO has £100

Method: 0/1 knapsack (dynamic programming, in pence) - the mathematically best basket that maximises total stars with total cost <= £100.

| # | Title | Price | Rating |
|---|---|---|---|
| 1 | Starving Hearts (Triangular Trade Trilogy, #1) | £13.99 | 2 |
| 2 | Set Me Free | £17.46 | 5 |
| 3 | The Four Agreements: A Practical Guide to Personal Freedom | £17.66 | 5 |
| 4 | Sophie's World | £15.94 | 5 |
| 5 | Untitled Collection: Sabbath Poems 2014 | £14.27 | 4 |
| 6 | Thirst | £17.27 | 5 |
| | **Total** | **£96.59** | **26** |

Books bought: 6 | Total cost: £96.59 | Money left: £3.41 | Total star score: 26

## Quick facts for the business recommendation

- 5-star books: 14 of 60 (23%), average price £32.48 vs £35.00 overall.
- 5-star books under £20: 4.
- Price range: £12.84 to £57.31.
