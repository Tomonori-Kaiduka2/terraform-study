import pytest
from playwright.sync_api import Page, expect

def test_streamlit_title(page: Page):
    # Streamlitが起動しているURLへアクセス
    page.goto("http://localhost:8501")

    # ページタイトル（ブラウザのタブ名）を確認
    expect(page).to_have_title("Streamlit")

    # 画面内に「Docker体験中！(v2)」という文字があるか確認
    expect(page.get_by_text("Docker体験中！(v2)")).to_be_visible()
