import httpx
from bs4 import BeautifulSoup

async def get_title_from_url(url: str) -> str | None:
    """
    Truy cập URL và lấy nội dung <title> của trang (nếu có).

    Args:
        url (str): Đường dẫn đến trang web.

    Returns:
        str | None: Tiêu đề trang, hoặc None nếu không lấy được.
    """
    try:
        async with httpx.AsyncClient(timeout=8.0, follow_redirects=True) as client:
            response = await client.get(url)
            response.raise_for_status()
            soup = BeautifulSoup(response.text, "html.parser")
            title_tag = soup.title
            return title_tag.string.strip() if title_tag and title_tag.string else None
    except Exception as e:
        print(f"[Lỗi lấy title]: {e}")
        return None
