from google_play_scraper import app, search
from .logger import Logger

def get(package_name: str):
    try:
        return app(
            package_name,
            lang='en',
            country='us'
        )
    except:
        Logger.error(f"Failed to find app with package {package_name}")

def find(keyword: str | None = None):
    if not keyword:
        return find(Logger.input("Search what in store"))

    return search(
        query=keyword,
        lang='en',
        country='us',
        n_hits=1
    )

__all__ = ['find', 'get']
