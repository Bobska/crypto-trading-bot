---
mode: agent
---
📊 VERSION 2.0: DJANGO WEB APP (THE UPGRADE)
Goal: Professional web application with full control and database.
What You'll Add:

✅ Start/Stop bot from web interface
✅ Change settings (thresholds, amounts)
✅ Full trade history with filters/search
✅ Database storage (SQLite → PostgreSQL later)
✅ Multiple pages (dashboard, trades, settings, logs)
✅ Better UI with templates and styling
✅ User authentication (optional)

New Project Structure:
C:\dev-projects\crypto-bot-ui\        # NEW Django project
├── manage.py
├── crypto_bot_ui\
│   ├── settings.py
│   ├── urls.py
│   └── wsgi.py
├── dashboard\                         # Main app
│   ├── models.py                      # Trade history model
│   ├── views.py                       # View functions
│   ├── urls.py
│   ├── api_client.py                  # Calls bot API
│   ├── templates\
│   │   ├── base.html
│   │   ├── dashboard.html
│   │   ├── trades.html
│   │   ├── settings.html
│   │   ├── controls.html
│   │   └── logs.html
│   └── static\
│       ├── css\
│       │   └── style.css
│       └── js\
│           └── dashboard.js
└── requirements.txt

🔧 STEP 1: Create Django Project
Manual steps:
bashcd C:\dev-projects
django-admin startproject crypto_bot_ui
cd crypto_bot_ui
python manage.py startapp dashboard
Copilot Prompt for requirements.txt:
Create requirements.txt for Django trading bot UI:
- Django>=5.0
- requests>=2.31.0  # For calling bot API
- python-dateutil>=2.8.2
- channels>=4.0.0  # For WebSocket (Phase 3)
- channels-redis>=4.1.0  # For WebSocket (Phase 3)
Install:
bashpip install -r requirements.txt

🔧 STEP 2: Configure Django Settings
Copilot Prompt to modify crypto_bot_ui/settings.py:
Update Django settings.py for trading bot dashboard:

In INSTALLED_APPS, add:
- 'dashboard',

In TEMPLATES, ensure:
- 'DIRS': [BASE_DIR / 'dashboard' / 'templates'],

Add at bottom:
- # Trading Bot API Configuration
- BOT_API_URL = 'http://localhost:8002/api'
- BOT_API_TIMEOUT = 5  # seconds

In ALLOWED_HOSTS, add:
- 'localhost', '127.0.0.1'

Set DEBUG = True for development

🔧 STEP 3: Create Trade History Model
Copilot Prompt for dashboard/models.py:
Create Django model for storing trade history:

Import:
- from django.db import models
- from django.utils import timezone

Model: Trade
- Fields:
  * timestamp (DateTimeField, default=timezone.now)
  * symbol (CharField, max_length=20, default='BTC/USDT')
  * action (CharField, max_length=4, choices=[('BUY','Buy'),('SELL','Sell')])
  * price (DecimalField, max_digits=12, decimal_places=2)
  * amount (DecimalField, max_digits=10, decimal_places=6)
  * profit_loss_pct (DecimalField, max_digits=5, decimal_places=2, null=True)
  * result (CharField, max_length=4, choices=[('WIN','Win'),('LOSS','Loss')], null=True)
- Meta:
  * ordering = ['-timestamp']  # Most recent first
- Method __str__: returns f"{self.action} {self.amount} {self.symbol} @ ${self.price}"
- Method is_win: returns self.result == 'WIN'

Model: BotSettings
- Fields:
  * buy_threshold (DecimalField, default=1.0)
  * sell_threshold (DecimalField, default=1.0)
  * trade_amount (DecimalField, default=0.001)
  * stop_loss_enabled (BooleanField, default=True)
  * stop_loss_pct (DecimalField, default=3.0)
  * trailing_stop_enabled (BooleanField, default=False)
  * trailing_stop_pct (DecimalField, default=2.0)
  * updated_at (DateTimeField, auto_now=True)
- Method save: overridden to ensure only one instance exists
- Class method get_settings: returns singleton instance
Run migrations:
bashpython manage.py makemigrations
python manage.py migrate

🔧 STEP 4: Create API Client Helper
Copilot Prompt for dashboard/api_client.py:
Create helper module to call trading bot API:

Import:
- import requests
- from django.conf import settings
- import logging

Class BotAPIClient:
- __init__: sets self.base_url = settings.BOT_API_URL

Method get_status():
- GET request to /api/status
- Returns dict with bot status or None on error
- Timeout = settings.BOT_API_TIMEOUT
- Logs errors

Method get_stats():
- GET request to /api/stats
- Returns statistics dict or None

Method get_recent_trades():
- GET request to /api/trades/recent
- Returns list of recent trades or empty list

Method start_bot():
- POST request to /api/bot/start
- Returns True on success, False on failure
- Logs result

Method stop_bot():
- POST request to /api/bot/stop
- Returns True on success, False on failure

Method update_settings(settings_dict):
- POST request to /api/settings
- Sends updated settings to bot
- Returns True on success

All methods include try/except with logging
All methods handle timeout and connection errors gracefully

🔧 STEP 5: Create Dashboard View
Copilot Prompt for dashboard/views.py:
Create Django views for trading bot dashboard:

Import:
- from django.shortcuts import render, redirect
- from django.contrib import messages
- from .api_client import BotAPIClient
- from .models import Trade, BotSettings

View: dashboard_view(request)
- Creates BotAPIClient instance
- Fetches status, stats, recent trades
- Context:
  * bot_status: dict from API
  * stats: dict from API
  * recent_trades: list (last 5)
  * page_title: "Dashboard"
- Renders 'dashboard.html'

View: trades_view(request)
- Gets all Trade objects from database (last 100)
- Optional filtering by:
  * Date range (request.GET.get('from_date'), 'to_date')
  * Action type ('action' - BUY/SELL)
  * Result ('result' - WIN/LOSS)
- Context:
  * trades: filtered queryset
  * total_trades: count
  * page_title: "Trade History"
- Renders 'trades.html'

View: settings_view(request)
- If GET: display current settings form
- If POST: update settings
  * Update BotSettings model
  * Call api_client.update_settings()
  * messages.success("Settings updated")
  * Redirect to settings page
- Context:
  * settings: BotSettings.get_settings()
  * page_title: "Settings"
- Renders 'settings.html'

View: controls_view(request)
- If POST with action='start': call api_client.start_bot()
- If POST with action='stop': call api_client.stop_bot()
- Add success/error message
- Redirect to dashboard
- If GET: render controls page
- Renders 'controls.html'

View: logs_view(request)
- Reads recent log file (last 100 lines)
- Context:
  * log_lines: list of strings
  * page_title: "Bot Logs"
- Renders 'logs.html'

🔧 STEP 6: Create URL Configuration
Copilot Prompt for dashboard/urls.py:
Create URL patterns for dashboard app:

Import:
- from django.urls import path
- from . import views

app_name = 'dashboard'

urlpatterns:
- path('', views.dashboard_view, name='dashboard')
- path('trades/', views.trades_view, name='trades')
- path('settings/', views.settings_view, name='settings')
- path('controls/', views.controls_view, name='controls')
- path('logs/', views.logs_view, name='logs')
Copilot Prompt to modify crypto_bot_ui/urls.py:
Update main urls.py to include dashboard URLs:

Import:
- from django.contrib import admin
- from django.urls import path, include
- from django.views.generic import RedirectView

urlpatterns:
- path('admin/', admin.site.urls)
- path('dashboard/', include('dashboard.urls'))
- path('', RedirectView.as_view(url='/dashboard/', permanent=False))

🔧 STEP 7: Create Base Template
Copilot Prompt for dashboard/templates/base.html:
Create base.html Django template with navigation:

Structure:
- <!DOCTYPE html> with responsive viewport
- <head>:
  * Title: "{% block title %}Trading Bot{% endblock %}"
  * Bootstrap 5 CSS CDN
  * Custom CSS (in {% block extra_css %})
- <body>:
  * Navigation bar with links:
    - Dashboard (home)
    - Trade History
    - Settings
    - Controls
    - Bot Logs
  * Container div for main content
  * {% block content %}{% endblock %}
  * Footer with copyright
  * Bootstrap JS CDN
  * jQuery CDN
  * Custom JS (in {% block extra_js %})

Styling:
- Dark theme (bg-dark, text-light)
- Active nav link highlighting
- Responsive navbar (collapses on mobile)
- Fixed top navbar
- Proper spacing for fixed nav (padding-top on body)

Django template tags:
- {% load static %}
- Use {% url %} for navigation links
- Add 'active' class if current page matches

🔧 STEP 8: Create Dashboard Template
Copilot Prompt for dashboard/templates/dashboard.html:
Create dashboard.html that extends base.html:

{% extends 'base.html' %}
{% block title %}Dashboard - Trading Bot{% endblock %}

Content structure:
- Header: <h1>🤖 Trading Bot Dashboard</h1>

- Status Card (top):
  * Bot Status: {{ bot_status.bot_running }} (🟢/🔴 emoji)
  * Symbol: {{ bot_status.symbol }}
  * Current Price: ${{ bot_status.current_price|floatformat:2 }}
  * Position: {{ bot_status.position }}
  * Last Updated: {{ bot_status.last_updated }}

- Balance Row (3 cards):
  * USDT Balance: ${{ bot_status.balance.USDT|floatformat:2 }}
  * BTC Balance: {{ bot_status.balance.BTC|floatformat:6 }} BTC
  * Total Value: Calculate and display

- Statistics Row (3 cards):
  * Total Trades: {{ stats.total_trades }}
  * Win Rate: {{ stats.win_rate|floatformat:1 }}%
  * Wins: {{ stats.wins }} | Losses: {{ stats.losses }}

- Recent Trades Table:
  * Table headers: Time | Action | Price | Result
  * Loop through recent_trades
  * Show last 5 trades
  * Color-code: green for wins, red for losses
  * Link to "View All Trades" page

- Quick Actions:
  * Buttons linking to Controls page
  * "Change Settings" button

Styling with Bootstrap:
- Use cards (card, card-body)
- Use row and col-md-4 for 3-column layout
- Use table table-dark table-striped
- Use btn btn-primary for buttons
- Add badge badge-success/danger for status

JavaScript (in extra_js block):
- Auto-refresh every 30 seconds
- location.reload() to refresh page
- Optional: AJAX to update without full reload

🔧 STEP 9: Create Other Templates
Copilot Prompt for remaining templates:
Create these templates extending base.html:

1. trades.html:
- Full trade history table
- Filter form at top (date range, action, result)
- Pagination (25 trades per page)
- Export to CSV button
- Summary stats at bottom

2. settings.html:
- Form for BotSettings model
- Number inputs for thresholds
- Checkboxes for enable/disable features
- "Save Settings" button
- Display current values in form
- Show last updated timestamp

3. controls.html:
- Large Start/Stop buttons
- Current bot status display
- Confirmation for stop action
- Recent activity log
- Emergency stop button (big, red)

4. logs.html:
- Display log file contents
- Monospace font
- Auto-scroll to bottom
- Refresh button
- Filter by log level (INFO, WARNING, ERROR)
- Color-coded log levels

All templates:
- Use Bootstrap styling
- Responsive design
- Include appropriate icons
- Add Django messages display (for success/error)

🔧 STEP 10: Add Static Files (CSS/JS)
Copilot Prompt for dashboard/static/css/style.css:
Create custom CSS for trading bot dashboard:

General styling:
- Dark theme variables (CSS custom properties)
- Card shadows and hover effects
- Smooth transitions on all elements
- Custom scrollbar styling (dark theme)

Status indicators:
- .status-running: green background with pulse animation
- .status-stopped: red background
- .status-badge: rounded pill shape

Trade table:
- .trade-win: light green background
- .trade-loss: light red background
- Hover effect on rows
- Alternating row colors

Buttons:
- .btn-start: large green button with icon
- .btn-stop: large red button with icon
- .btn-emergency: bright red, pulsing animation
- Hover and active states

Cards:
- Custom card styling
- Gradient backgrounds for stats cards
- Animated number counters (optional)

Responsive design:
- Mobile-friendly breakpoints
- Collapsible sidebar on mobile
- Touch-friendly button sizes
Copilot Prompt for dashboard/static/js/dashboard.js:
Create JavaScript for enhanced dashboard functionality:

Function: formatCurrency(value)
- Adds $ and commas
- Returns formatted string

Function: formatPercent(value)
- Adds % and + for positive
- Color codes (green/red)

Function: animateNumber(element, start, end, duration)
- Animates number counting up
- Used for stats display

Function: updatePriceColor(newPrice, oldPrice)
- Flashes green if price increased
- Flashes red if price decreased
- Visual feedback for price changes

Function: autoRefresh(intervalSeconds)
- Reloads page periodically
- Shows countdown timer
- Allows user to pause auto-refresh

Function: confirmStop()
- Confirmation dialog for stopping bot
- Returns true/false

Export functions:
- Export trade history to CSV
- Download functionality

Real-time clock:
- Updates "Last Updated" timestamp
- Shows time since last update

Event listeners:
- Page load initialization
- Button click handlers
- Form submission handlers

✅ VERSION 2.0 CHECKPOINT
Test it works:

✅ Django server running: python manage.py runserver 8001
✅ Bot API running: python bot_api.py (port 8002)
✅ Trading bot running: python main.py
✅ Open http://localhost:8001 in browser
✅ Navigate through all pages
✅ Start/stop bot from web interface
✅ Change settings and see them apply
✅ View trade history with filters

What you have now:

Professional web application
Full bot control (start/stop/settings)
Database storage of trades
Multi-page navigation
Better organization and scalability
Still using 30-second refresh

Limitations:

Not real-time (30-second delay)
Page reloads for updates
No live trade notifications

Time to complete: 1 week (part-time work)