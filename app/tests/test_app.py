import pytest
from pathlib import Path
from playwright.sync_api import Page, expect

SCREENSHOT_DIR = Path(__file__).resolve().parent / "screenshots"

@pytest.fixture(autouse=True)
def ensure_screenshot_dir():
    SCREENSHOT_DIR.mkdir(parents=True, exist_ok=True)
    yield


def test_streamlit_title(page: Page):
    # Streamlitが起動しているURLへアクセス
    page.goto("http://localhost:8501")

    try:
        # ページタイトル（ブラウザのタブ名）を確認
        expect(page).to_have_title("Streamlit")

        # 画面内に「Docker体験中！(v2)」という文字があるか確認
        expect(page.get_by_text("Docker体験中！(v2)")).to_be_visible()
    finally:
        page.screenshot(path=str(SCREENSHOT_DIR / "streamlit_page.png"), full_page=True)
