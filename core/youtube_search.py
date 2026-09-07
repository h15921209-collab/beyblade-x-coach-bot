import urllib.request
import urllib.parse
import re
import json
import time
import logging
from typing import List, Dict, Any

logger = logging.getLogger("core.youtube_search")

# In-memory search cache: query -> (timestamp, results)
_CACHE: Dict[str, tuple[float, List[Dict[str, Any]]]] = {}
CACHE_TTL = 3600  # 1 hour

def search_beyblade_videos(query_text: str, max_results: int = 3) -> List[Dict[str, Any]]:
    """
    Searches YouTube for videos related to the given Beyblade X combo or query.
    Returns a list of dicts with:
    - video_id: str
    - title: str
    - channel: str
    - duration: str
    - url: str
    - thumbnail: str
    """
    clean_query = query_text.strip()
    if not clean_query:
        return []

    # Format search keywords for high relevance
    search_term = f"戰鬥陀螺X {clean_query} 實戰 對戰"
    if "戰鬥陀螺" in clean_query or "Beyblade" in clean_query:
        search_term = clean_query

    # Check cache
    now = time.time()
    if search_term in _CACHE:
        ts, cached_res = _CACHE[search_term]
        if now - ts < CACHE_TTL:
            return cached_res[:max_results]

    try:
        encoded = urllib.parse.quote(search_term)
        url = f"https://www.youtube.com/results?search_query={encoded}"
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
            "Accept-Language": "zh-TW,zh;q=0.9,en-US;q=0.8,en;q=0.7"
        }
        req = urllib.request.Request(url, headers=headers)
        with urllib.request.urlopen(req, timeout=5) as resp:
            html = resp.read().decode("utf-8", errors="ignore")

        # Extract ytInitialData
        pattern = r"var ytInitialData = ({.*?});</script>"
        match = re.search(pattern, html)
        if not match:
            # Alternate pattern
            match = re.search(r"window\[\"ytInitialData\"\] = ({.*?});", html)

        results = []
        if match:
            data = json.loads(match.group(1))
            sections = (
                data.get("contents", {})
                .get("twoColumnSearchResultsRenderer", {})
                .get("primaryContents", {})
                .get("sectionListRenderer", {})
                .get("contents", [])
            )
            for section in sections:
                items = section.get("itemSectionRenderer", {}) .get("contents", [])
                for item in items:
                    v = item.get("videoRenderer")
                    if v:
                        vid = v.get("videoId")
                        title_runs = v.get("title", {}).get("runs", [])
                        title = "".join([r.get("text", "") for r in title_runs]).strip()
                        channel_runs = v.get("ownerText", {}).get("runs", [])
                        channel = "".join([r.get("text", "") for r in channel_runs]).strip()
                        duration = v.get("lengthText", {}).get("simpleText", "精華短片")
                        
                        # Filter out YouTube Shorts or invalid video IDs
                        if vid and title and len(vid) == 11:
                            # Use YouTube HQ thumbnail or default to webp
                            thumb = f"https://i.ytimg.com/vi/{vid}/hqdefault.jpg"
                            results.append({
                                "video_id": vid,
                                "title": title,
                                "channel": channel or "陀螺競技精選",
                                "duration": duration,
                                "url": f"https://www.youtube.com/watch?v={vid}",
                                "thumbnail": thumb
                            })
                            if len(results) >= max_results:
                                break
                if len(results) >= max_results:
                    break

        # Save to cache
        if results:
            _CACHE[search_term] = (now, results)
        return results[:max_results]

    except Exception as e:
        logger.warning(f"Error during YouTube search for '{search_term}': {e}")
        return []
