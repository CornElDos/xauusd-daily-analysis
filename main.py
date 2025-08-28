# main.py - XAUUSD Daily Analysis Automation
import os
import asyncio
import aiohttp
import smtplib
import schedule
import time
from datetime import datetime
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from anthropic import Anthropic

from http.server import HTTPServer, BaseHTTPRequestHandler
import threading

class HealthHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        if self.path == '/':
            self.send_response(200)
            self.send_header('Content-type', 'text/plain')
            self.end_headers()
            self.wfile.write(b'XAUUSD Analysis Service - Running')
        else:
            self.send_response(404)
            self.end_headers()

def start_health_server():
    server = HTTPServer(('', int(os.getenv('PORT', 8080))), HealthHandler)
    server_thread = threading.Thread(target=server.serve_forever)
    server_thread.daemon = True
    server_thread.start()
    print(f"Health server started on port {os.getenv('PORT', 8080)}")

class XAUUSDAnalyzer:
    def __init__(self):
        # Environment variables (set in Railway dashboard)
        self.anthropic_client = Anthropic(api_key=os.getenv('ANTHROPIC_API_KEY'))
        self.smtp_server = os.getenv('SMTP_SERVER', 'smtp.gmail.com')
        self.smtp_port = int(os.getenv('SMTP_PORT', '587'))
        self.email_user = os.getenv('EMAIL_USER')
        self.email_password = os.getenv('EMAIL_PASSWORD')
        self.recipients = os.getenv('EMAIL_RECIPIENTS', '').split(',')
        
    def get_analysis_prompt(self):
        """The complete analysis prompt from our previous work"""
        return """
        When analyzing XAUUSD, provide a comprehensive trading analysis following this exact 4-part structure. Always search for current market data and today's economic events.

        PART 1: 📊 TEKNISK ANALYS
        1. VOLUME-ANALYS: Analyze volume patterns vs price movements, identify spikes, look for divergences
        2. KRITISKA NIVÅER: Major resistance, current support, key support, deeper support with specific price ranges
        3. KONKRET STRATEGI: Primary bias, entry points, stop loss, targets with R/R ratios, timeframe
        4. SANNOLIKHETER: Percentage probabilities for different scenarios with timeframes
        5. WARNING SIGNALS: What would invalidate strategy, key levels, volume patterns, external factors
        6. RIGHT NOW POSITION: Current recommendation (Long/Short/Neutral), size (1-10), reasoning

        PART 2: 📅 DAGENS HÄNDELSER & RISKER
        - 🚨 HIGH IMPACT: Major economic data, central bank speeches, geopolitical events
        - 📊 MID IMPACT: Secondary indicators, technical tests, Fed rate changes, COT data
        - ⚡ LOW IMPACT: Minor releases, retail sentiment, technical patterns
        - 🎯 IMPACT PÅ XAUUSD: Positive/Negative/Neutral factors

        PART 3: 📱 TELEGRAM SIGNAL
        Format as copy-paste ready signal with:
        - Current price & bias with probability
        - Primary setup (entry/SL/TP)
        - Alternative setup if applicable
        - Key levels and timeframes
        - Most likely outcome

        PART 4: Brief description of the most likely visual setup for traders

        Focus on actionable trading information with specific price levels, realistic probabilities, and short-term scalping/day trading setups. Use Swedish for main analysis, technical terms in English when appropriate.
        """

    async def get_current_xauusd_data(self):
        """Fetch current XAUUSD price and market data"""
        try:
            async with aiohttp.ClientSession() as session:
                # You can use various free APIs here
                # For example: Alpha Vantage, Financial Modeling Prep, etc.
                # This is a placeholder - replace with actual API
                async with session.get('https://api.example.com/xauusd') as response:
                    if response.status == 200:
                        data = await response.json()
                        return data
                    return None
        except Exception as e:
            print(f"Error fetching market data: {e}")
            return None

    async def generate_analysis(self):
        """Generate the complete XAUUSD analysis"""
        try:
            # Get current market data
            market_data = await self.get_current_xauusd_data()
            
            # Create analysis prompt with current data
            current_date = datetime.now().strftime("%B %d, %Y")
            analysis_prompt = f"""
            Today is {current_date}. Please provide a complete XAUUSD analysis following the established 4-part structure.
            
            Current market context: {market_data if market_data else 'Please search for current XAUUSD price and market sentiment'}
            
            {self.get_analysis_prompt()}
            
            Focus on actionable setups for the next 4-8 hours of trading.
            """
            
            # Generate analysis using Claude
            response = self.anthropic_client.messages.create(
                model="claude-3-5-sonnet-20241022",
                max_tokens=4000,
                temperature=0.1,
                messages=[{"role": "user", "content": analysis_prompt}]
            )
            
            return response.content[0].text
            
        except Exception as e:
            error_msg = f"Error generating analysis: {e}"
            print(error_msg)
            return error_msg

    def format_email_html(self, analysis_text):
        """Format the analysis as HTML email"""
        html_template = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <meta charset="UTF-8">
            <style>
                body {{ font-family: Arial, sans-serif; line-height: 1.6; color: #333; }}
                .header {{ background-color: #1a1a1a; color: #64f4ac; padding: 20px; text-align: center; }}
                .content {{ padding: 20px; background-color: #f9f9f9; }}
                .telegram-box {{ background-color: #0088cc; color: white; padding: 15px; margin: 20px 0; border-radius: 8px; }}
                .warning {{ background-color: #ff4757; color: white; padding: 10px; border-radius: 5px; margin: 10px 0; }}
                .success {{ background-color: #2ed573; color: white; padding: 10px; border-radius: 5px; margin: 10px 0; }}
                pre {{ background-color: #f4f4f4; padding: 10px; border-radius: 5px; overflow-x: auto; }}
            </style>
        </head>
        <body>
            <div class="header">
                <h1>🥇 XAUUSD Daily Analysis</h1>
                <p>{datetime.now().strftime("%Y-%m-%d %H:%M")} Swedish Time</p>
            </div>
            <div class="content">
                <pre>{analysis_text}</pre>
                <div class="warning">
                    <strong>⚠️ Risk Warning:</strong> This analysis is for educational purposes only. 
                    Trading involves substantial risk. Never risk more than you can afford to lose.
                </div>
            </div>
        </body>
        </html>
        """
        return html_template

    async def send_analysis_email(self, analysis):
        """Send analysis via email"""
        try:
            if not self.email_user or not self.email_password:
                print("Email credentials not configured")
                return False

            # Create message
            msg = MIMEMultipart('alternative')
            msg['Subject'] = f"🥇 XAUUSD Analysis - {datetime.now().strftime('%Y-%m-%d')}"
            msg['From'] = self.email_user
            msg['To'] = ', '.join(self.recipients)

            # Create HTML content
            html_content = self.format_email_html(analysis)
            html_part = MIMEText(html_content, 'html')
            msg.attach(html_part)

            # Send email
            with smtplib.SMTP(self.smtp_server, self.smtp_port) as server:
                server.starttls()
                server.login(self.email_user, self.email_password)
                server.send_message(msg)

            print(f"✅ Analysis email sent successfully to {len(self.recipients)} recipients")
            return True

        except Exception as e:
            print(f"❌ Error sending email: {e}")
            return False

    async def run_daily_analysis(self):
        """Main function to run daily analysis"""
        print(f"🚀 Starting XAUUSD analysis at {datetime.now()}")
        
        # Generate analysis
        analysis = await self.generate_analysis()
        
        if "Error" not in analysis:
            # Send email
            await self.send_analysis_email(analysis)
            print("📧 Daily analysis completed successfully")
        else:
            print(f"❌ Analysis failed: {analysis}")

def schedule_daily_analysis():
    """Schedule the daily analysis"""
    analyzer = XAUUSDAnalyzer()
    
    # Schedule for 07:30 Swedish time (05:30 UTC)
    schedule.every().day.at("05:30").do(
        lambda: asyncio.run(analyzer.run_daily_analysis())
    )
    
    print("📅 Scheduler started - Daily analysis at 07:30 Swedish time")
    
    # Keep the script running
    while True:
        schedule.run_pending()
        time.sleep(60)  # Check every minute

if __name__ == "__main__":
    # Debug: print environment variables
    print(f"TEST_MODE value: '{os.getenv('TEST_MODE')}'")
    print(f"All env vars: {dict(os.environ)}")
    
    # Check for test mode (more robust checking)
    test_mode = os.getenv('TEST_MODE', '').lower() in ['true', '1', 'yes']
    
    if test_mode:
        print("🧪 Running in TEST MODE - executing analysis immediately")
        analyzer = XAUUSDAnalyzer()
        asyncio.run(analyzer.run_daily_analysis())
    else:
        print("📅 Running in SCHEDULED MODE - waiting for 07:30")
        schedule_daily_analysis()
