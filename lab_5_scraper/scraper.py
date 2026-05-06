"""
Crawler implementation.
"""

# pylint: disable=too-many-arguments, too-many-instance-attributes, unused-import, undefined-variable, unused-argument
import datetime
import json
import pathlib
import re

import requests
from bs4 import BeautifulSoup, Tag

from core_utils.article.article import Article
from core_utils.config_dto import ConfigDTO

from core_utils.constants import CRAWLER_CONFIG_PATH, ASSETS_PATH

class IncorrectSeedURLError(Exception):
    """Exception raised when seed URL does not match standard pattern \"https?://(www.)?\""""

class NumberOfArticlesOutOfRangeError(Exception):
    """Exception raised when total number of articles is out of range from 1 to 150"""

class IncorrectNumberOfArticlesError(Exception):
    """Exception raised when total number of articles to parse is not integer or less than 0"""

class IncorrectHeadersError(Exception):
    """Exception raised when headers are not in a form of dictionary"""

class IncorrectEncodingError(Exception):
    """Exception raised when encoding is not specified as a string"""

class IncorrectTimeoutError(Exception):
    """Exception raised when timeout value is not a positive integer less than 60"""

class IncorrectVerifyError(Exception):
    """Exception raised when certificate or headless mode values must are not either True or False"""

class Config:
    """
    Class for unpacking and validating configurations.
    """
    
    _path_to_config : pathlib.Path
    _config_values : ConfigDTO

    def __init__(self, path_to_config: pathlib.Path) -> None:
        """
        Initialize an instance of the Config class.

        Args:
            path_to_config (pathlib.Path): Path to configuration.
        """
        
        self._path_to_config = path_to_config
        self._config_values = self._extract_config_content()

        self._validate_config_content()

    def _extract_config_content(self) -> ConfigDTO:
        """
        Get config values.

        Returns:
            ConfigDTO: Config values
        """

        with open(self._path_to_config, encoding="utf-8") as config_file:
            config_data = json.load(config_file)
            return ConfigDTO(config_data["seed_urls"], config_data["total_articles_to_find_and_parse"], config_data["headers"], config_data["encoding"], config_data["timeout"], config_data["should_verify_certificate"], config_data["headless_mode"])


    def _validate_config_content(self) -> None:
        """
        Ensure configuration parameters are not corrupt.
        """
        

        for url in self._config_values.seed_urls:
            if not re.match("https?://(www.)?", url):
                raise IncorrectSeedURLError()

        if not isinstance(self._config_values.total_articles, int) or isinstance(self._config_values.total_articles, bool) or self._config_values.total_articles < 0:
            raise IncorrectNumberOfArticlesError()

        if not (1 <= self._config_values.total_articles < 150):
            raise NumberOfArticlesOutOfRangeError()
    
        if not isinstance(self._config_values.headers, dict):
            raise IncorrectHeadersError()

        if not isinstance(self._config_values.encoding, str):
            raise IncorrectEncodingError()
    
        if not isinstance(self._config_values.timeout, int) or isinstance(self._config_values.timeout, bool) or self._config_values.timeout < 0 or self._config_values.timeout > 60:
            raise IncorrectEncodingError()
    
        if not isinstance(self._config_values.headless_mode, bool) or not isinstance(self._config_values.should_verify_certificate, bool):
            raise IncorrectVerifyError()


    def get_seed_urls(self) -> list[str]:
        """
        Retrieve seed urls.

        Returns:
            list[str]: Seed urls
        """

        return self._config_values.seed_urls

    def get_num_articles(self) -> int:
        """
        Retrieve total number of articles to scrape.

        Returns:
            int: Total number of articles to scrape
        """

        return self._config_values.total_articles

    def get_headers(self) -> dict[str, str]:
        """
        Retrieve headers to use during requesting.

        Returns:
            dict[str, str]: Headers
        """

        return self._config_values.headers

    def get_encoding(self) -> str:
        """
        Retrieve encoding to use during parsing.

        Returns:
            str: Encoding
        """

        return self._config_values.encoding

    def get_timeout(self) -> int:
        """
        Retrieve number of seconds to wait for response.

        Returns:
            int: Number of seconds to wait for response
        """
        
        return self._config_values.timeout

    def get_verify_certificate(self) -> bool:
        """
        Retrieve whether to verify certificate.

        Returns:
            bool: Whether to verify certificate or not
        """

        return self._config_values.should_verify_certificate

    def get_headless_mode(self) -> bool:
        """
        Retrieve whether to use headless mode.

        Returns:
            bool: Whether to use headless mode or not
        """

        return self._config_values.headless_mode


def make_request(url: str, config: Config) -> requests.models.Response:
    """
    Deliver a response from a request with given configuration.

    Args:
        url (str): Site url
        config (Config): Configuration

    Returns:
        requests.models.Response: A response from a request
    """

    return requests.get(url, headers=config.get_headers(), timeout=config.get_timeout())


class Crawler:
    """
    Crawler implementation.
    """

    _config : Config
    urls = []

    #: Url pattern
    url_pattern: re.Pattern | str

    def __init__(self, config: Config) -> None:
        """
        Initialize an instance of the Crawler class.

        Args:
            config (Config): Configuration
        """

        self._config = config
        self.find_articles()

    def _extract_url(self, article_bs: Tag):
        """
        Find and retrieve urls from HTML.

        Args:
            article_bs (bs4.Tag): Tag instance

        Returns:
            list[str]: Urls from HTML
        """

        return "https://theatre-library.ru" + article_bs.find("a")["href"]
        

    def find_articles(self) -> None:
        """
        Find articles.
        """

        for article_url in self.get_search_urls():
            response = make_request(article_url, self._config)

            if not response.ok:
                continue
            
            

            soup = BeautifulSoup(response.text, features="lxml")

            for article_bs in soup.find_all(class_="th_d1"):
                self.urls.append(self._extract_url(article_bs))


    def get_search_urls(self) -> list:
        """
        Get seed_urls param.

        Returns:
            list: seed_urls param
        """

        return self._config.get_seed_urls()


# 10


class CrawlerRecursive(Crawler):
    """
    Recursive implementation.

    Get one URL of the title page and find requested number of articles recursively.
    """

    def __init__(self, config: Config) -> None:
        """
        Initialize an instance of the CrawlerRecursive class.

        Args:
            config (Config): Configuration
        """

    def find_articles(self) -> None:
        """
        Find number of article urls requested.
        """


# 4, 6, 8, 10


class HTMLParser:
    """
    HTMLParser implementation.
    """

    def __init__(self, full_url: str, article_id: int, config: Config) -> None:
        """
        Initialize an instance of the HTMLParser class.

        Args:
            full_url (str): Site url
            article_id (int): Article id
            config (Config): Configuration
        """

    def _fill_article_with_text(self, article_soup: BeautifulSoup) -> None:
        """
        Find text of article.

        Args:
            article_soup (bs4.BeautifulSoup): BeautifulSoup instance
        """

    def _fill_article_with_meta_information(self, article_soup: BeautifulSoup) -> None:
        """
        Find meta information of article.

        Args:
            article_soup (bs4.BeautifulSoup): BeautifulSoup instance
        """

    def unify_date_format(self, date_str: str) -> datetime.datetime:
        """
        Unify date format.

        Args:
            date_str (str): Date in text format

        Returns:
            datetime.datetime: Datetime object
        """

    def parse(self) -> Article | bool:
        """
        Parse each article.

        Returns:
            Article | bool: Article instance, False in case of request error
        """


def prepare_environment(base_path: pathlib.Path | str) -> None:
    """
    Create ASSETS_PATH folder if no created and remove existing folder.

    Args:
        base_path (pathlib.Path | str): Path where articles stores
    """

    if base_path.exists():
        for stored_file in base_path.iterdir():
            stored_file.unlink()

        base_path.rmdir()
    
    base_path.mkdir(parents=True)


def main() -> None:
    """
    Entrypoint for scraper module.
    """

    configuration = Config(path_to_config=CRAWLER_CONFIG_PATH)
    prepare_environment(ASSETS_PATH)
    crawler = Crawler(config=configuration)

if __name__ == "__main__":
    main()
