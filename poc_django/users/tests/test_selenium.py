# ref: https://ordinarycoders.com/blog/article/testing-django-selenium
# There is an auto version
# https://pypi.org/project/chromedriver-binary/
from allauth.utils import get_user_model
from chromedriver_binary import chromedriver_filename
from django.urls import reverse
from django.test import LiveServerTestCase
from selenium import webdriver
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from selenium.common.exceptions import TimeoutException
from selenium.webdriver.chrome.options import Options
from urllib.parse import urljoin


User = get_user_model()


class CredentialsData:
    email = "user@email.com"
    username = "user"
    password = User.objects.make_random_password()

# Do we really need to start the server?
class LoginTest(LiveServerTestCase, CredentialsData):
    def setUp(self) -> None:
        chrome_options = Options()
        chrome_options.add_argument('--disable-gpu')
        chrome_options.add_argument('--headless')

        # if error: https://stackoverflow.com/questions/50138615/webdriverexception-unknown-error-cannot-find-chrome-binary-error-with-selenium
        self.browser = webdriver.Chrome(chrome_options=chrome_options, executable_path=chromedriver_filename)
        return super().setUp()

    def waitPageLoading(self) -> None:
        TIMEOUT_DELAY = 3
        try:
            WebDriverWait(self.browser, TIMEOUT_DELAY).until(EC.presence_of_element_located((By.TAG_NAME, 'html')))
        except TimeoutException:
            return

    def test_signup(self):
        self.browser.get(urljoin(self.live_server_url, reverse('account_signup')))

        contents = {
            "id_email": self.email,
            "id_username": self.username,
            "id_password1": self.password,
            "id_password2": self.password,
        }

        self.waitPageLoading()

        for field_id, field_content in contents.items():
            self.browser.find_element(By.ID, field_id).send_keys(field_content)

        self.browser.find_element(By.CSS_SELECTOR , 'button[type="submit"]').click()

        assert f'Confirmation e-mail sent to {self.email}' in self.browser.page_source
        assert User.objects.count() == 1

    def test_login(self):
        assert User.objects.count() == 0

        self.browser.get(urljoin(self.live_server_url, reverse('account_login')))
        
        contents = {
            "id_login": self.username,
            "id_password": self.password,
        }

        self.waitPageLoading()

        for field_id, field_content in contents.items():
            self.browser.find_element(By.ID, field_id).send_keys(field_content)

        self.browser.find_element(By.CSS_SELECTOR , 'button[type="submit"]').click()

        assert f'The username and/or password you specified are not correct.' in self.browser.page_source


        # ------ Now with User
        User.objects.create_user(email=self.email, username=self.username, password=self.password)
        assert User.objects.count() == 1

        self.browser.get(urljoin(self.live_server_url, reverse('account_login')))

        contents = {
            "id_login": self.username,
            "id_password": self.password,
        }

        self.waitPageLoading()

        for field_id, field_content in contents.items():
            self.browser.find_element(By.ID, field_id).send_keys(field_content)

        self.browser.find_element(By.CSS_SELECTOR , 'button[type="submit"]').click()

        assert f'The username and/or password you specified are not correct.' not in self.browser.page_source
        assert f'Verify Your E-mail Address' in self.browser.page_source
