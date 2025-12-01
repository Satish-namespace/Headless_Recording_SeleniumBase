from seleniumbase import BaseCase
import time

class TestQuotes(BaseCase):   # <-- must start with 'Test'
    headless = False
    width = 1920
    height = 1080

    def test_quotes_scraping(self):
        self.open("https://quotes.toscrape.com/")
        self.assert_title("Quotes to Scrape")
        time.sleep(5)
        self.assert_element(".quote")
        first_quote = self.get_text(".quote span.text")
        first_author = self.get_text(".quote small.author")
        print(f"First Quote: {first_quote} - {first_author}")
        self.click(".next a")
        time.sleep(5)
        self.assert_element(".quote")
        assert False
