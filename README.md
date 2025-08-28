# 🥇 XAUUSD Daily Analysis Automation

Automated daily gold (XAU/USD) trading analysis using Claude AI, deployed on Railway with email delivery.

## 🎯 Features

- **Daily Analysis:** Complete technical and fundamental analysis every morning at 07:30 Swedish time
- **4-Part Structure:** Technical analysis, market events, telegram signals, visual setups  
- **Email Delivery:** HTML-formatted analysis sent to subscribers
- **High Accuracy:** Proven track record with minimal stop losses
- **Real-time Data:** Fetches current market conditions and economic events

## 📊 Analysis Includes

### 📈 Technical Analysis
- Volume analysis with divergence detection
- Critical support/resistance levels
- Concrete trading strategies with R/R ratios
- Probability assessments for different scenarios
- Warning signals and invalidation levels

### 📅 Market Events
- High/medium/low impact economic events
- Fed policy implications
- Geopolitical risk assessment
- COT (Commitment of Traders) insights

### 📱 Trading Signals
- Copy-paste ready Telegram format
- Specific entry/exit levels
- Stop loss recommendations
- Time-based trade management

## 🚂 Deployment

### Railway (Primary)
1. Fork this repository
2. Connect to Railway
3. Set environment variables
4. Auto-deploys on git push

### GitHub Actions (Backup)
- Runs parallel to Railway
- Manual trigger available
- Artifact logging for debugging

## 🔧 Environment Variables

```env
ANTHROPIC_API_KEY=your_claude_api_key
SMTP_SERVER=smtp.gmail.com
SMTP_PORT=587
EMAIL_USER=your_email@gmail.com
EMAIL_PASSWORD=your_gmail_app_password
EMAIL_RECIPIENTS=email1@domain.com,email2@domain.com
