"""
Web search tool with live DuckDuckGo HTML results.
"""

import html
import json
import re
from urllib import parse, request


class WebTool:
    def _clean_text(self, raw: str) -> str:
        text = re.sub(r"<.*?>", "", raw)
        return html.unescape(text).strip()

    def _is_version_query(self, query: str) -> bool:
        q = query.lower()
        version_tokens = ["surum", "version", "release", "en guncel", "latest", "guncel"]
        return any(t in q for t in version_tokens)

    def _fedora_latest_from_official_api(self) -> str:
        """
        endoflife.date keeps distro release data up to date and machine-readable.
        """
        api_url = "https://endoflife.date/api/fedora.json"
        with request.urlopen(api_url, timeout=15) as response:
            data = json.loads(response.read().decode("utf-8"))
        latest = data[0]
        cycle = latest.get("cycle", "?")
        release_date = latest.get("releaseDate", "?")
        return (
            "[WebTool] Resmi release verisi:\n"
            f"- En guncel Fedora surumu: Fedora {cycle}\n"
            f"- Yayin tarihi: {release_date}\n"
            "- Kaynak: https://endoflife.date/fedora"
        )

    def search_and_summarize(self, query: str) -> str:
        q_lower = query.lower()

        # Prefer official release feed for Fedora version questions.
        if "fedora" in q_lower and self._is_version_query(query):
            try:
                return self._fedora_latest_from_official_api()
            except Exception:  # noqa: BLE001
                # Fall back to general search below.
                pass

        # Use HTML search endpoint to get fresher top results.
        url = "https://html.duckduckgo.com/html/?" + parse.urlencode({"q": query})
        headers = {
            "User-Agent": (
                "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                "AppleWebKit/537.36 (KHTML, like Gecko) "
                "Chrome/124.0.0.0 Safari/537.36"
            )
        }
        req = request.Request(url, headers=headers)

        try:
            with request.urlopen(req, timeout=20) as response:
                page = response.read().decode("utf-8", errors="ignore")
        except Exception as exc:  # noqa: BLE001
            return f"[WebTool] Arama basarisiz: {exc}"

        titles = re.findall(
            r'<a[^>]*class="result__a"[^>]*>(.*?)</a>',
            page,
            flags=re.IGNORECASE | re.DOTALL,
        )
        snippets = re.findall(
            r'<a[^>]*class="result__snippet"[^>]*>(.*?)</a>',
            page,
            flags=re.IGNORECASE | re.DOTALL,
        )
        links = re.findall(
            r'<a[^>]*class="result__url"[^>]*>(.*?)</a>',
            page,
            flags=re.IGNORECASE | re.DOTALL,
        )

        top_n = min(5, len(titles))
        if top_n == 0:
            return "[WebTool] Sonuc bulunamadi."

        lines = ["[WebTool] Canli arama sonuclari:"]
        for i in range(top_n):
            title = self._clean_text(titles[i])
            snippet = self._clean_text(snippets[i]) if i < len(snippets) else ""
            link = self._clean_text(links[i]) if i < len(links) else ""
            lines.append(f"{i + 1}) {title}")
            if snippet:
                lines.append(f"   - {snippet}")
            if link:
                lines.append(f"   - Kaynak: https://{link.lstrip('/')}")

        return "\n".join(lines)

