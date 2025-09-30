#!/usr/bin/env python3

import http.server
import socketserver
import threading
import time
from playwright.sync_api import sync_playwright
import requests

def test_server_connection():
    """Test if the React dev server is accessible"""
    try:
        response = requests.get('http://localhost:3000/app/', timeout=5)
        print(f"Server test: Status {response.status_code}")
        return True
    except requests.exceptions.ConnectionError:
        print("Server test: Connection refused")
        return False
    except Exception as e:
        print(f"Server test: Error {e}")
        return False

# Test the authentication flow using real browser automation
def test_react_app_auth():
    with sync_playwright() as p:
        # Launch a browser
        browser = p.chromium.launch(headless=False)
        context = browser.new_context()
        page = context.new_page()
        
        # Enable console logging
        page.on('console', lambda msg: print(f'Console: {msg.type}: {msg.text}'))
        page.on('pageerror', lambda error: print(f'Page Error: {error}'))
        
        try:
            # Navigate to the React app
            print("Navigating to React app...")
            page.goto('http://localhost:3000/app/')
            
            # Wait for the page to load
            page.wait_for_load_state('networkidle')
            
            print("Page loaded successfully!")
            print("Current URL:", page.url)
            
            # Try to find and click login/signup buttons
            print("Looking for login elements...")
            
            # Wait a bit for React to render
            time.sleep(2)
            
            # Take a screenshot for debugging
            page.screenshot(path='react_app_screenshot.png')
            print("Screenshot saved as react_app_screenshot.png")
            
            # Try to find login form
            login_form = page.locator('form')
            if login_form.count() > 0:
                print(f"Found {login_form.count()} form(s)")
                
                # Look for email and password inputs
                email_input = page.locator('input[type="email"], input[name="email"]')
                password_input = page.locator('input[type="password"], input[name="password"]')
                
                if email_input.count() > 0 and password_input.count() > 0:
                    print("Found login form, trying to login...")
                    
                    # Fill the form
                    email_input.fill('test2@example.com')
                    password_input.fill('testpassword123')
                    
                    # Submit the form
                    submit_button = page.locator('button[type="submit"]').first()
                    if submit_button.count() > 0:
                        print("Clicking submit button...")
                        submit_button.click()
                        
                        # Wait for navigation or response
                        page.wait_for_load_state('networkidle')
                        time.sleep(2)
                        
                        # Check if login was successful
                        current_url = page.url
                        print(f"After login URL: {current_url}")
                        
                        # Take another screenshot
                        page.screenshot(path='after_login_screenshot.png')
                        print("After-login screenshot saved as after_login_screenshot.png")
                        
                    else:
                        print("No submit button found")
                else:
                    print("No login inputs found")
            else:
                print("No forms found")
            
            # Keep browser open for a while to observe
            print("Keeping browser open for 10 seconds...")
            time.sleep(10)
            
        except Exception as e:
            print(f"Error during test: {e}")
        finally:
            browser.close()

if __name__ == "__main__":
    print("Testing server connection first...")
    if test_server_connection():
        print("Server is accessible, starting Playwright test...")
        test_react_app_auth()
    else:
        print("Server is not accessible, skipping Playwright test.")