import requests
from bs4 import BeautifulSoup
import psycopg2
import os
import sys

# Database configuration from environment variables
DB_CONFIG = {
    'host': os.getenv('DB_HOST', 'psql-db'),
    'port': os.getenv('DB_PORT', '5432'),
    'dbname': os.getenv('DB_NAME', 'postgres'),
    'user': os.getenv('DB_USER', 'postgres'),
    'password': os.getenv('DB_PASSWORD', '123456'),
}

BLOG_URL = 'https://www.python.org/blogs/'


def scrape_blog_posts():
    """Scrape blog posts from Python Insider."""
    try:
        response = requests.get(BLOG_URL, timeout=30)
        response.raise_for_status()
    except requests.RequestException as e:
        print(f"Error fetching {BLOG_URL}: {e}")
        sys.exit(1)

    soup = BeautifulSoup(response.content, 'html.parser')
    posts = []

    # Scrape featured post (the main highlighted post)
    featured = soup.find('div', class_='shrubbery')
    if featured:
        title_tag = featured.find('h2')
        if title_tag:
            link = title_tag.find('a')
            title = link.text.strip() if link else title_tag.text.strip()
            date_tag = featured.find('time')
            date = date_tag.text.strip() if date_tag else 'Unknown'
            author_tag = featured.find('span', class_='author')
            author = author_tag.text.strip() if author_tag else 'Unknown'
            posts.append({
                'title': title,
                'publication_date': date,
                'author': author,
            })

    # Scrape latest news section
    news_section = soup.find('div', id='newslist')
    if news_section:
        for item in news_section.find_all('li'):
            title_tag = item.find('a')
            title = title_tag.text.strip() if title_tag else 'Unknown'
            date_tag = item.find('time')
            date = date_tag.text.strip() if date_tag else 'Unknown'
            author_tag = item.find('span', class_='author')
            author = author_tag.text.strip() if author_tag else 'Unknown'
            posts.append({
                'title': title,
                'publication_date': date,
                'author': author,
            })

    print(f"Scraped {len(posts)} blog posts")
    return posts


def create_table(conn):
    """Create blog_posts table if not exists."""
    with conn.cursor() as cur:
        cur.execute('''
            CREATE TABLE IF NOT EXISTS blog_posts (
                id SERIAL PRIMARY KEY,
                title VARCHAR(500) NOT NULL UNIQUE,
                publication_date VARCHAR(100) NOT NULL,
                author VARCHAR(200),
                scraped_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
    conn.commit()
    print("Table 'blog_posts' created/verified")


def insert_posts(conn, posts):
    """Insert posts into the database."""
    with conn.cursor() as cur:
        for post in posts:
            cur.execute('''
                INSERT INTO blog_posts (title, publication_date, author)
                VALUES (%s, %s, %s)
                ON CONFLICT (title) DO NOTHING
            ''', (post['title'], post['publication_date'], post['author']))
    conn.commit()
    print(f"Inserted {len(posts)} posts into database")


def get_connection():
    """Get database connection."""
    try:
        conn = psycopg2.connect(**DB_CONFIG)
        print(f"Connected to database at {DB_CONFIG['host']}:{DB_CONFIG['port']}")
        return conn
    except psycopg2.OperationalError as e:
        print(f"Error connecting to database: {e}")
        sys.exit(1)


def main():
    """Main entry point."""
    print("Starting Python Insider blog scraper...")
    posts = scrape_blog_posts()

    if not posts:
        print("No posts found. Exiting.")
        sys.exit(1)

    conn = get_connection()
    try:
        create_table(conn)
        insert_posts(conn, posts)
        print("Scraping completed successfully!")
    finally:
        conn.close()
        print("Database connection closed")


if __name__ == '__main__':
    main()
