from playwright.sync_api import Page, expect


def test_chromium_renders_a_page(page: Page) -> None:
    page.set_content("<h1>hello</h1>")

    expect(page.locator("h1")).to_have_text("hello")
