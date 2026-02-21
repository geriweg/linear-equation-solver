import pytest
import threading
import uvicorn
import time
from api.index import app
from playwright.sync_api import Page, expect

# Host and port for the test server
HOST = "127.0.0.1"
PORT = 8001
URL = f"http://{HOST}:{PORT}"

def run_server():
    uvicorn.run(app, host=HOST, port=PORT, log_level="error")

@pytest.fixture(scope="session", autouse=True)
def server():
    # Start the server in a background thread
    thread = threading.Thread(target=run_server, daemon=True)
    thread.start()
    # Wait for server to start
    time.sleep(2)
    yield
    # No explicit stop needed as daemon=True

def test_ui_solve_equation(page: Page):
    # Navigate to the app
    # Since we are testing UI, we need to serve the static file.
    # For simplicity in this test, we navigate directly to the API health to check server,
    # but the real UI test needs the index.html.
    # I'll modify the index.py temporarily or add a route to serve the static file for the test.
    pass

@app.get("/")
async def serve_index():
    from fastapi.responses import FileResponse
    return FileResponse("public/index.html")

def test_ui_full_flow(page: Page):
    page.goto(URL)
    
    # Check title
    expect(page.locator("h1")).to_contain_text("Gleichungslöser")
    
    # Fill in equation
    page.fill("#equation", "2x + 10 = 20")
    
    # Click solve
    page.click("#solveBtn")
    
    # Wait for result
    res_full = page.locator("#resFull")
    expect(res_full).to_be_visible()
    expect(res_full).to_have_text("x = 5")

def test_ui_error_flow(page: Page):
    page.goto(URL)
    
    # Fill in invalid equation
    page.fill("#equation", "x + y = 10")
    page.click("#solveBtn")
    
    # Check error message
    error_msg = page.locator("#errorMsg")
    expect(error_msg).to_be_visible()
    expect(error_msg).to_contain_text("eine Variable")
