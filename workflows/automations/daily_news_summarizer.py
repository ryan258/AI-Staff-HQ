# To use this script, you need to install the feedparser library:
# pip install feedparser

import feedparser

def summarize_rss_feed(feed_url, num_articles=5):
    """Fetches the latest articles from an RSS feed and provides a summary."""
    feed = feedparser.parse(feed_url)
    summary = []
    for entry in feed.entries[:num_articles]:
        summary.append(f"- {entry.title}: {entry.link}")
    return "\n".join(summary)

if __name__ == '__main__':
    import argparse

    parser = argparse.ArgumentParser(description='Summarize an RSS feed.')
    parser.add_argument('feed_url', type=str, help='The URL of the RSS feed.')
    parser.add_argument('--num_articles', type=int, default=5, help='The number of articles to summarize.')

    args = parser.parse_args()
    summary = summarize_rss_feed(args.feed_url, args.num_articles)
    print(summary)
