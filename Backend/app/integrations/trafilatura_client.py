
import ipaddress
import socket
from urllib.parse import urlparse

import httpx
import trafilatura


def validate_article_url(url: str) -> str:
    """
    Validate article URLs and block private or unsafe destinations.
    """

    parsed_url = urlparse(url)

    if parsed_url.scheme != "https":
        raise ValueError("Only HTTPS article URLs are allowed")

    if not parsed_url.hostname:
        raise ValueError("Invalid article URL")

    if parsed_url.username or parsed_url.password:
        raise ValueError("URLs containing credentials are not allowed")

    hostname = parsed_url.hostname

    try:
        ip_addresses = socket.getaddrinfo(
            hostname,
            None,
            type=socket.SOCK_STREAM,
        )

        for address in ip_addresses:
            ip = ipaddress.ip_address(address[4][0])

            if not ip.is_global:
                raise ValueError("Private or restricted URLs are not allowed")

    except socket.gaierror:
        raise ValueError("Unable to resolve article URL")

    return url


def extract_article(url: str) -> dict:
    """
    Download and extract readable article content.
    """

    validated_url = validate_article_url(url)

    try:
        with httpx.Client(
            timeout=15.0,
            follow_redirects=False,
            headers={
                "User-Agent": "InfoLens/1.0 Article Extractor",
            },
            trust_env=False,
        ) as client:

            response = client.get(validated_url)
            response.raise_for_status()

            content_type = response.headers.get(
                "content-type",
                "",
            ).lower()

            if "text/html" not in content_type:
                raise ValueError("URL does not contain an HTML article")

            downloaded_content = response.text

        extracted_content = trafilatura.extract(
            downloaded_content,
            include_comments=False,
            include_tables=True,
            favor_precision=True,
        )

        if not extracted_content:
            raise ValueError("Unable to extract article content")

        metadata = trafilatura.extract_metadata(
            downloaded_content,
        )

        return {
            "url": validated_url,
            "title": metadata.title if metadata else None,
            "author": metadata.author if metadata else None,
            "date": metadata.date if metadata else None,
            "content": extracted_content,
        }

    except httpx.HTTPError as exc:
        raise ValueError("Unable to download article") from exc
