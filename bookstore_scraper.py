"""
Assignment 2 - The Bookstore Intelligence Mission
Business Data and Text Mining | Web Scraping

Name        : Asad Riaz
Roll Number : 22i-0651
Section     : BSBA - A

What this program does
----------------------
1. Scrapes book listings (Title, Price, Rating, Availability, Product URL)
   from https://books.toscrape.com/ using requests + BeautifulSoup.
2. Uses ONE reusable function inside a loop to scrape several catalogue pages
   (default: 3 pages; --pages 5 for Bonus 1, --pages all to scrape the whole catalogue).
3. Cleans the data (price -> float, rating word -> number 1-5) and stores it in
   a Pandas DataFrame, saved as competitor_books.csv.
4. Answers the seven intelligence-analysis questions, solves the CEO £100
   challenge (0/1 knapsack), counts books per star level and draws a bar chart.
5. Writes every answer to analysis_results.md so nothing is typed by hand.

Run:
    pip install -r requirements.txt
    python bookstore_scraper.py            # 3 pages (required)
    python bookstore_scraper.py --pages 5  # Bonus 1
    python bookstore_scraper.py --pages all  # Boss level: every page
"""

import argparse
import re
import time
from urllib.parse import urljoin

import matplotlib

matplotlib.use("Agg")  # save the chart to a file without needing a screen
import matplotlib.pyplot as plt
import pandas as pd
import requests
from bs4 import BeautifulSoup

STUDENT = {"name": "Asad Riaz", "roll": "22i-0651", "section": "BSBA - A"}

START_URL = "https://books.toscrape.com/catalogue/page-1.html"
HEADERS = {"User-Agent": "Mozilla/5.0 (student web-scraping assignment)"}

# The site stores the rating as a CSS class word, e.g. <p class="star-rating Three">
RATING_MAP = {"One": 1, "Two": 2, "Three": 3, "Four": 4, "Five": 5}

BUDGET = 100.00  # CEO challenge budget in £


# ---------------------------------------------------------------------------
# Mission 2 - capture the data from ONE page
# ---------------------------------------------------------------------------
def scrape_page(page_url):
    """Download one catalogue page and return (list_of_books, next_page_url)."""
    response = requests.get(page_url, headers=HEADERS, timeout=20)
    response.raise_for_status()
    response.encoding = "utf-8"  # otherwise '£' can appear as 'Â£'
    soup = BeautifulSoup(response.text, "html.parser")

    books = []
    for card in soup.find_all("article", class_="product_pod"):
        link = card.h3.a
        title = link["title"]  # full title (the visible text is shortened with '...')

        price_text = card.find("p", class_="price_color").get_text(strip=True)
        price = float(re.sub(r"[^0-9.]", "", price_text))  # '£51.77' -> 51.77

        rating_classes = card.find("p", class_="star-rating")["class"]
        rating_word = next(c for c in rating_classes if c in RATING_MAP)
        rating = RATING_MAP[rating_word]  # 'Three' -> 3

        availability = card.find("p", class_="availability").get_text(strip=True)

        product_url = urljoin(page_url, link["href"])  # Bonus 2

        books.append(
            {
                "Title": title,
                "Price": price,
                "Rating": rating,
                "Availability": availability,
                "Product_URL": product_url,
            }
        )

    next_link = soup.select_one("li.next a")
    next_url = urljoin(page_url, next_link["href"]) if next_link else None
    return books, next_url


# ---------------------------------------------------------------------------
# Mission 3 - scale the operation with a loop (same function, many pages)
# ---------------------------------------------------------------------------
def scrape_catalogue(max_pages=3, start_url=START_URL, delay=0.5):
    """Follow the 'next' button page after page until max_pages (None = all)."""
    all_books = []
    url = start_url
    page_number = 0

    while url and (max_pages is None or page_number < max_pages):
        page_number += 1
        books, url = scrape_page(url)
        all_books.extend(books)
        print(f"Page {page_number}: scraped {len(books)} books")
        time.sleep(delay)  # be polite to the server

    return pd.DataFrame(all_books)


def clean(df):
    """Basic cleaning: trim text, fix types, drop duplicates/empty rows."""
    df = df.copy()
    df["Title"] = df["Title"].str.strip()
    df["Availability"] = df["Availability"].str.strip()
    df["Price"] = df["Price"].astype(float)
    df["Rating"] = df["Rating"].astype(int)
    df = df.dropna(subset=["Title", "Price", "Rating"])
    df = df.drop_duplicates(subset=["Product_URL"]).reset_index(drop=True)
    return df


# ---------------------------------------------------------------------------
# Final challenge - CEO has £100 (0/1 knapsack: maximise total stars)
# ---------------------------------------------------------------------------
def ceo_challenge(df, budget=BUDGET):
    """Pick books that maximise the total star rating with cost <= budget.

    Works in pence so prices are exact integers. Dynamic programming:
    best[c] = highest total rating achievable with total cost exactly <= c.
    If several baskets tie on stars, the cheapest one is chosen.
    """
    prices = (df["Price"] * 100).round().astype(int).tolist()
    ratings = df["Rating"].tolist()
    cap = int(round(budget * 100))
    n = len(prices)

    best = [0] * (cap + 1)
    took = [bytearray(cap + 1) for _ in range(n)]
    for i in range(n):
        p, r = prices[i], ratings[i]
        for c in range(cap, p - 1, -1):
            if best[c - p] + r > best[c]:
                best[c] = best[c - p] + r
                took[i][c] = 1

    max_stars = best[cap]
    c = min(x for x in range(cap + 1) if best[x] == max_stars)  # cheapest tie
    chosen = []
    for i in range(n - 1, -1, -1):
        if took[i][c]:
            chosen.append(i)
            c -= prices[i]

    basket = df.loc[sorted(chosen), ["Title", "Price", "Rating"]].reset_index(drop=True)
    return basket


# ---------------------------------------------------------------------------
# Mission 4 - intelligence analysis
# ---------------------------------------------------------------------------
def analyse(df):
    results = {}
    results["most_expensive"] = df.loc[df["Price"].idxmax()]
    results["cheapest"] = df.loc[df["Price"].idxmin()]
    results["average_price"] = df["Price"].mean()
    results["five_star_count"] = int((df["Rating"] == 5).sum())
    in_stock = df["Availability"].str.contains("In stock", case=False)
    results["in_stock_pct"] = in_stock.mean() * 100
    # Many books share the top rating, so ties are broken by the lower price
    results["top5"] = df.sort_values(["Rating", "Price"], ascending=[False, True]).head(5)
    five = df[df["Rating"] == 5]
    results["cheapest_five_star"] = five.loc[five["Price"].idxmin()]
    results["rating_counts"] = df["Rating"].value_counts().sort_index()  # Bonus 3
    results["avg_price_by_rating"] = df.groupby("Rating")["Price"].mean().round(2)
    results["basket"] = ceo_challenge(df)
    return results


def save_chart(rating_counts, path="rating_counts.png"):
    """Bonus 4 - bar chart of how many books sit at each star level."""
    fig, ax = plt.subplots(figsize=(7, 4.5))
    bars = ax.bar(rating_counts.index.astype(str), rating_counts.values, color="#2f6f9f")
    ax.bar_label(bars, padding=3)
    ax.set_xlabel("Star rating")
    ax.set_ylabel("Number of books")
    ax.set_title(f"Competitor books by star rating (n = {rating_counts.sum()})")
    ax.spines[["top", "right"]].set_visible(False)
    fig.tight_layout()
    fig.savefig(path, dpi=150)
    plt.close(fig)


def gbp(x):
    return f"£{x:.2f}"


def write_report(df, r, pages_label, path="analysis_results.md"):
    """Write every answer to a Markdown file (generated, not typed by hand)."""
    basket = r["basket"]
    five = df[df["Rating"] == 5]
    lines = [
        "# Bookstore Intelligence - Analysis Results",
        "",
        f"**Name:** {STUDENT['name']} | **Roll No:** {STUDENT['roll']} | "
        f"**Section:** {STUDENT['section']}",
        "",
        f"Dataset: {len(df)} books scraped from {pages_label} of books.toscrape.com "
        "(generated automatically by bookstore_scraper.py).",
        "",
        "## Mission 4 - Intelligence Analysis",
        "",
        f"1. **Most expensive book:** {r['most_expensive']['Title']} - "
        f"{gbp(r['most_expensive']['Price'])} ({r['most_expensive']['Rating']} stars)",
        f"2. **Cheapest book:** {r['cheapest']['Title']} - {gbp(r['cheapest']['Price'])} "
        f"({r['cheapest']['Rating']} stars)",
        f"3. **Average book price:** {gbp(r['average_price'])}",
        f"4. **Books with a 5-star rating:** {r['five_star_count']}",
        f"5. **Books in stock:** {r['in_stock_pct']:.1f}%",
        "6. **Top 5 highest-rated books** (all 5 stars; ties broken by lowest price):",
        "",
        "   | # | Title | Price | Rating |",
        "   |---|---|---|---|",
    ]
    for i, row in enumerate(r["top5"].itertuples(), 1):
        lines.append(f"   | {i} | {row.Title} | {gbp(row.Price)} | {row.Rating} |")
    lines += [
        "",
        f"7. **Cheapest 5-star book:** {r['cheapest_five_star']['Title']} - "
        f"{gbp(r['cheapest_five_star']['Price'])}",
        "",
        "## Bonus 3 - Books per star rating",
        "",
        "| Rating | Books | Average price |",
        "|---|---|---|",
    ]
    for rating, count in r["rating_counts"].items():
        lines.append(f"| {rating} | {count} | {gbp(r['avg_price_by_rating'][rating])} |")
    lines += [
        "",
        "![Rating counts](rating_counts.png)",
        "",
        "## Final Challenge - The CEO has £100",
        "",
        "Method: 0/1 knapsack (dynamic programming, in pence) - the mathematically "
        "best basket that maximises total stars with total cost <= £100.",
        "",
        "| # | Title | Price | Rating |",
        "|---|---|---|---|",
    ]
    for i, row in enumerate(basket.itertuples(), 1):
        lines.append(f"| {i} | {row.Title} | {gbp(row.Price)} | {row.Rating} |")
    lines += [
        f"| | **Total** | **{gbp(basket['Price'].sum())}** | **{basket['Rating'].sum()}** |",
        "",
        f"Books bought: {len(basket)} | Total cost: {gbp(basket['Price'].sum())} | "
        f"Money left: {gbp(BUDGET - basket['Price'].sum())} | "
        f"Total star score: {basket['Rating'].sum()}",
        "",
        "## Quick facts for the business recommendation",
        "",
        f"- 5-star books: {len(five)} of {len(df)} ({len(five) / len(df) * 100:.0f}%), "
        f"average price {gbp(five['Price'].mean())} vs {gbp(df['Price'].mean())} overall.",
        f"- 5-star books under £20: {int((five['Price'] < 20).sum())}.",
        f"- Price range: {gbp(df['Price'].min())} to {gbp(df['Price'].max())}.",
    ]
    with open(path, "w", encoding="utf-8") as f:
        f.write("\n".join(lines) + "\n")


def main():
    parser = argparse.ArgumentParser(description="Scrape books.toscrape.com")
    parser.add_argument("--pages", default="3", help="number of pages, or 'all'")
    parser.add_argument("--start-url", default=START_URL, help=argparse.SUPPRESS)
    args = parser.parse_args()
    max_pages = None if args.pages.lower() == "all" else int(args.pages)

    print(f"{STUDENT['name']} | {STUDENT['roll']} | {STUDENT['section']}")
    df = clean(scrape_catalogue(max_pages=max_pages, start_url=args.start_url))

    print("\nFirst rows of the dataset:")
    print(df[["Title", "Price", "Rating", "Availability"]].head())
    print("\nColumn types:")
    print(df.dtypes)

    df.to_csv("competitor_books.csv", index=False, encoding="utf-8-sig")
    print(f"\nSaved {len(df)} books to competitor_books.csv")

    r = analyse(df)
    save_chart(r["rating_counts"])
    pages_label = "all pages" if max_pages is None else f"{max_pages} pages"
    write_report(df, r, pages_label)

    print("\n--- Intelligence analysis ---")
    print("1. Most expensive:", r["most_expensive"]["Title"], gbp(r["most_expensive"]["Price"]))
    print("2. Cheapest:", r["cheapest"]["Title"], gbp(r["cheapest"]["Price"]))
    print("3. Average price:", gbp(r["average_price"]))
    print("4. 5-star books:", r["five_star_count"])
    print(f"5. In stock: {r['in_stock_pct']:.1f}%")
    print("6. Top 5 highest-rated:")
    print(r["top5"][["Title", "Price", "Rating"]].to_string(index=False))
    print("7. Cheapest 5-star:", r["cheapest_five_star"]["Title"],
          gbp(r["cheapest_five_star"]["Price"]))
    print("\nBooks per rating (Bonus 3):")
    print(r["rating_counts"].to_string())
    basket = r["basket"]
    print("\n--- CEO £100 challenge ---")
    print(basket.to_string(index=False))
    print(f"Total cost: {gbp(basket['Price'].sum())} | Total stars: {basket['Rating'].sum()}")
    print("\nSaved: competitor_books.csv, rating_counts.png, analysis_results.md")


if __name__ == "__main__":
    main()
