import pytest
from unittest.mock import patch, Mock
from web_scraping_sample import scrape_blog_posts

MOCK_HTML = '''
<html>
<body>
    <div class="shrubbery">
        <h2><a href="/blog/post1">Python 3.14 Released</a></h2>
        <time>Aug. 19, 2026</time>
        <span class="author">Written by Guido van Rossum</span>
    </div>
    <div id="newslist">
        <li>
            <a>Python 3.12.14 Available</a>
            <time>Aug. 12, 2026</time>
            <span class="author">Written by Python Team</span>
        </li>
        <li>
            <a>Python 3.14.7 Released</a>
            <time>Aug. 5, 2026</time>
            <span class="author">Written by Python Team</span>
        </li>
    </div>
</body>
</html>
'''


@patch('web_scraping_sample.requests.get')
def test_scrape_blog_posts_returns_list(mock_get):
    """Test that scrape_blog_posts returns a list."""
    mock_response = Mock()
    mock_response.content = MOCK_HTML.encode()
    mock_response.raise_for_status = Mock()
    mock_get.return_value = mock_response

    posts = scrape_blog_posts()
    assert isinstance(posts, list)
    assert len(posts) == 3


@patch('web_scraping_sample.requests.get')
def test_scrape_blog_posts_extracts_title(mock_get):
    """Test that titles are extracted correctly."""
    mock_response = Mock()
    mock_response.content = MOCK_HTML.encode()
    mock_response.raise_for_status = Mock()
    mock_get.return_value = mock_response

    posts = scrape_blog_posts()
    assert posts[0]['title'] == 'Python 3.14 Released'
    assert posts[1]['title'] == 'Python 3.12.14 Available'


@patch('web_scraping_sample.requests.get')
def test_scrape_blog_posts_extracts_date(mock_get):
    """Test that dates are extracted correctly."""
    mock_response = Mock()
    mock_response.content = MOCK_HTML.encode()
    mock_response.raise_for_status = Mock()
    mock_get.return_value = mock_response

    posts = scrape_blog_posts()
    assert posts[0]['publication_date'] == 'Aug. 19, 2026'
    assert posts[1]['publication_date'] == 'Aug. 12, 2026'


@patch('web_scraping_sample.requests.get')
def test_scrape_blog_posts_extracts_author(mock_get):
    """Test that authors are extracted correctly."""
    mock_response = Mock()
    mock_response.content = MOCK_HTML.encode()
    mock_response.raise_for_status = Mock()
    mock_get.return_value = mock_response

    posts = scrape_blog_posts()
    assert posts[0]['author'] == 'Written by Guido van Rossum'
    assert posts[1]['author'] == 'Written by Python Team'


@patch('web_scraping_sample.requests.get')
def test_scrape_blog_posts_handles_network_error(mock_get):
    """Test that network errors are handled."""
    import requests
    mock_get.side_effect = requests.RequestException("Connection failed")

    with pytest.raises(SystemExit):
        scrape_blog_posts()
