from seleniumbase import BaseCase
import time

class TestNavigation(BaseCase):
    headless = False

    def test_google_visit(self):
        self.open("https://www.google.com")
        self.assert_title_contains("Google")
        time.sleep(2)
