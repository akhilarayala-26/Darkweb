from collect_links import collect_links
from scrape_data import scrape_data
# from process_fingerprints import process_scraped_data
from process_fingerprints import process_fingerprints_from_mongo

from filter_by_title import group_links_by_title_from_db, save_grouped_titles


def main():
    print("=== Step 1: Collecting Onion Links ===")
    collect_links()  # Now stores directly in MongoDB ("links_data")

    print("=== Step 2: Scraping Onion Data ===")
    scrape_data()  # Reads from MongoDB links_data, stores in scraped_data

    print("=== Step 3: Processing Fingerprints & Classification ===")

    process_fingerprints_from_mongo()
    
    print("=== Step 4: Grouping by Title ===")
    grouped = group_links_by_title_from_db()
    save_grouped_titles(grouped)

    
    print("\nAll done ✅")
    print("MongoDB Collections Updated:")
    print("- links_data")
    print("- scraped_data")
    print("- fingerprints")
    print("- grouped_titles")


if __name__ == "__main__":
    main()
