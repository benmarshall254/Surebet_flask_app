from flask import Flask, render_template_string, jsonify, request
from datetime import datetime, timedelta
import json

app = Flask(__name__)

# Sample data structure for predictions
SAMPLE_PREDICTIONS = [
    {
        "id": 1,
        "match": "Manchester United vs Chelsea",
        "league": "Premier League",
        "date": "2025-06-10",
        "time": "15:00",
        "prediction": "Over 2.5 Goals",
        "odds": "1.85",
        "confidence": "High",
        "status": "active"
    },
    {
        "id": 2,
        "match": "Barcelona vs Real Madrid",
        "league": "La Liga",
        "date": "2025-06-11",
        "time": "20:00",
        "prediction": "Both Teams to Score",
        "odds": "1.72",
        "confidence": "Medium",
        "status": "active"
    },
    {
        "id": 3,
        "match": "Bayern Munich vs Dortmund",
        "league": "Bundesliga",
        "date": "2025-06-12",
        "time": "18:30",
        "prediction": "Home Win",
        "odds": "2.10",
        "confidence": "High",
        "status": "active"
    }
]

NAVIGATION_TEMPLATE = """
<nav class="navbar">
    <div class="nav-container">
        <div class="nav-logo">
            <h2>🎯 SureBet Pro</h2>
        </div>
        <ul class="nav-menu">
            <li class="nav-item">
                <a href="/" class="nav-link">Home</a>
            </li>
            <li class="nav-item">
                <a href="/predictions" class="nav-link">Predictions</a>
            </li>
            <li class="nav-item">
                <a href="/statistics" class="nav-link">Statistics</a>
            </li>
            <li class="nav-item">
                <a href="/about" class="nav-link">About</a>
            </li>
        </ul>
    </div>
</nav>
"""

BASE_STYLES = """
<style>
    * {
        margin: 0;
        padding: 0;
        box-sizing: border-box;
    }

    body {
        font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        min-height: 100vh;
        color: #333;
        line-height: 1.6;
    }

    .container {
        max-width: 1200px;
        margin: 0 auto;
        padding: 0 20px;
    }

    /* Navigation Styles */
    .navbar {
        background: rgba(255, 255, 255, 0.95);
        backdrop-filter: blur(10px);
        box-shadow: 0 2px 20px rgba(0, 0, 0, 0.1);
        position: sticky;
        top: 0;
        z-index: 1000;
    }

    .nav-container {
        max-width: 1200px;
        margin: 0 auto;
        padding: 1rem 20px;
        display: flex;
        justify-content: space-between;
        align-items: center;
    }

    .nav-logo h2 {
        color: #667eea;
        font-weight: 700;
    }

    .nav-menu {
        display: flex;
        list-style: none;
        gap: 2rem;
    }

    .nav-link {
        text-decoration: none;
        color: #333;
        font-weight: 500;
        transition: color 0.3s ease;
    }

    .nav-link:hover {
        color: #667eea;
    }

    /* Main Content Styles */
    .main-content {
        padding: 2rem 0;
    }

    .hero-section {
        background: rgba(255, 255, 255, 0.1);
        backdrop-filter: blur(10px);
        border-radius: 20px;
        padding: 3rem;
        text-align: center;
        margin: 2rem 0;
        border: 1px solid rgba(255, 255, 255, 0.2);
    }

    .hero-title {
        font-size: 3rem;
        color: white;
        margin-bottom: 1rem;
        text-shadow: 2px 2px 4px rgba(0, 0, 0, 0.3);
    }

    .hero-subtitle {
        font-size: 1.2rem;
        color: rgba(255, 255, 255, 0.9);
        margin-bottom: 2rem;
    }

    .cta-button {
        background: linear-gradient(45deg, #667eea, #764ba2);
        color: white;
        padding: 1rem 2rem;
        border: none;
        border-radius: 50px;
        font-size: 1.1rem;
        font-weight: 600;
        cursor: pointer;
        transition: transform 0.3s ease, box-shadow 0.3s ease;
        text-decoration: none;
        display: inline-block;
    }

    .cta-button:hover {
        transform: translateY(-2px);
        box-shadow: 0 10px 30px rgba(0, 0, 0, 0.3);
    }

    /* Card Styles */
    .card {
        background: rgba(255, 255, 255, 0.95);
        border-radius: 15px;
        padding: 2rem;
        margin: 1rem 0;
        box-shadow: 0 8px 25px rgba(0, 0, 0, 0.1);
        transition: transform 0.3s ease;
    }

    .card:hover {
        transform: translateY(-5px);
    }

    .card-grid {
        display: grid;
        grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
        gap: 2rem;
        margin: 2rem 0;
    }

    .prediction-card {
        background: linear-gradient(135deg, #f8f9fa 0%, #e9ecef 100%);
        border-left: 4px solid #667eea;
        padding: 1.5rem;
        border-radius: 10px;
        margin: 1rem 0;
    }

    .match-info {
        font-size: 1.1rem;
        font-weight: 600;
        color: #333;
        margin-bottom: 0.5rem;
    }

    .league-info {
        color: #666;
        font-size: 0.9rem;
        margin-bottom: 1rem;
    }

    .prediction-details {
        display: flex;
        justify-content: space-between;
        align-items: center;
        flex-wrap: wrap;
        gap: 1rem;
    }

    .prediction-type {
        background: #667eea;
        color: white;
        padding: 0.5rem 1rem;
        border-radius: 20px;
        font-size: 0.9rem;
        font-weight: 500;
    }

    .odds-info {
        font-size: 1.2rem;
        font-weight: 700;
        color: #28a745;
    }

    .confidence-badge {
        padding: 0.3rem 0.8rem;
        border-radius: 15px;
        font-size: 0.8rem;
        font-weight: 600;
    }

    .confidence-high {
        background: #d4edda;
        color: #155724;
    }

    .confidence-medium {
        background: #fff3cd;
        color: #856404;
    }

    .confidence-low {
        background: #f8d7da;
        color: #721c24;
    }

    /* Statistics Styles */
    .stats-container {
        display: grid;
        grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
        gap: 1.5rem;
        margin: 2rem 0;
    }

    .stat-card {
        background: rgba(255, 255, 255, 0.95);
        padding: 1.5rem;
        border-radius: 10px;
        text-align: center;
        box-shadow: 0 4px 15px rgba(0, 0, 0, 0.1);
    }

    .stat-number {
        font-size: 2.5rem;
        font-weight: 700;
        color: #667eea;
        display: block;
    }

    .stat-label {
        color: #666;
        font-size: 0.9rem;
        margin-top: 0.5rem;
    }

    /* Footer Styles */
    .footer {
        background: rgba(0, 0, 0, 0.8);
        color: white;
        text-align: center;
        padding: 2rem 0;
        margin-top: 3rem;
    }

    /* Ad Styles */
    .ad-container {
        margin: 2rem 0;
        text-align: center;
    }

    .ad-label {
        font-size: 0.8rem;
        color: #666;
        margin-bottom: 0.5rem;
    }

    /* Responsive Design */
    @media (max-width: 768px) {
        .nav-menu {
            gap: 1rem;
        }

        .hero-title {
            font-size: 2rem;
        }

        .hero-section {
            padding: 2rem;
        }

        .card-grid {
            grid-template-columns: 1fr;
        }
    }
</style>
"""

@app.route("/")
def home():
    return render_template_string(f"""
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>SureBet Pro - Professional Betting Predictions</title>
        <meta name="description" content="Get professional surebet predictions with high accuracy rates. Daily football betting tips and analysis.">
        
        <!-- Google AdSense -->
        <script async src="https://pagead2.googlesyndication.com/pagead/js/adsbygoogle.js?client=ca-pub-6332657251575161"
            crossorigin="anonymous"></script>
        
        {BASE_STYLES}
    </head>
    <body>
        {NAVIGATION_TEMPLATE}
        
        <div class="container">
            <div class="main-content">
                <div class="hero-section">
                    <h1 class="hero-title">🎯 SureBet Pro</h1>
                    <p class="hero-subtitle">Professional betting predictions with proven accuracy</p>
                    <a href="/predictions" class="cta-button">View Today's Predictions</a>
                </div>

                <!-- Top Banner Ad -->
                <div class="ad-container">
                    <div class="ad-label">Advertisement</div>
                    <ins class="adsbygoogle"
                        style="display:block"
                        data-ad-client="ca-pub-6332657251575161"
                        data-ad-slot="1509818329"
                        data-ad-format="auto"
                        data-full-width-responsive="true"></ins>
                </div>

                <div class="card-grid">
                    <div class="card">
                        <h3>🏆 High Accuracy</h3>
                        <p>Our predictions are based on advanced statistical analysis and expert knowledge, delivering consistent results.</p>
                    </div>
                    
                    <div class="card">
                        <h3>📊 Daily Updates</h3>
                        <p>Fresh predictions every day covering major leagues and tournaments worldwide.</p>
                    </div>
                    
                    <div class="card">
                        <h3>💡 Expert Analysis</h3>
                        <p>Detailed match analysis with confidence ratings to help you make informed decisions.</p>
                    </div>
                </div>

                <!-- Mid-content Ad -->
                <div class="ad-container">
                    <div class="ad-label">Advertisement</div>
                    <ins class="adsbygoogle"
                        style="display:block"
                        data-ad-client="ca-pub-6332657251575161"
                        data-ad-slot="1509818329"
                        data-ad-format="auto"
                        data-full-width-responsive="true"></ins>
                </div>
            </div>
        </div>

        <div class="footer">
            <div class="container">
                <p>&copy; 2025 SureBet Pro. All rights reserved. | Bet responsibly.</p>
            </div>
        </div>

        <script>
            (adsbygoogle = window.adsbygoogle || []).push({{}});
            (adsbygoogle = window.adsbygoogle || []).push({{}});
        </script>
    </body>
    </html>
    """)

@app.route("/predictions")
def predictions():
    return render_template_string(f"""
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>Today's Predictions - SureBet Pro</title>
        
        <!-- Google AdSense -->
        <script async src="https://pagead2.googlesyndication.com/pagead/js/adsbygoogle.js?client=ca-pub-6332657251575161"
            crossorigin="anonymous"></script>
        
        {BASE_STYLES}
    </head>
    <body>
        {NAVIGATION_TEMPLATE}
        
        <div class="container">
            <div class="main-content">
                <div class="hero-section">
                    <h1 class="hero-title">📈 Today's Predictions</h1>
                    <p class="hero-subtitle">Updated: {datetime.now().strftime('%B %d, %Y at %H:%M')}</p>
                </div>

                <!-- Top Ad -->
                <div class="ad-container">
                    <div class="ad-label">Advertisement</div>
                    <ins class="adsbygoogle"
                        style="display:block"
                        data-ad-client="ca-pub-6332657251575161"
                        data-ad-slot="1509818329"
                        data-ad-format="auto"
                        data-full-width-responsive="true"></ins>
                </div>

                <div class="predictions-container">
                    {''.join([f'''
                    <div class="prediction-card">
                        <div class="match-info">{pred["match"]}</div>
                        <div class="league-info">{pred["league"]} • {pred["date"]} at {pred["time"]}</div>
                        <div class="prediction-details">
                            <div class="prediction-type">{pred["prediction"]}</div>
                            <div class="odds-info">Odds: {pred["odds"]}</div>
                            <div class="confidence-badge confidence-{pred["confidence"].lower()}">{pred["confidence"]} Confidence</div>
                        </div>
                    </div>
                    ''' for pred in SAMPLE_PREDICTIONS])}
                </div>

                <!-- Bottom Ad -->
                <div class="ad-container">
                    <div class="ad-label">Advertisement</div>
                    <ins class="adsbygoogle"
                        style="display:block"
                        data-ad-client="ca-pub-6332657251575161"
                        data-ad-slot="1509818329"
                        data-ad-format="auto"
                        data-full-width-responsive="true"></ins>
                </div>
            </div>
        </div>

        <div class="footer">
            <div class="container">
                <p>&copy; 2025 SureBet Pro. All rights reserved. | Bet responsibly.</p>
            </div>
        </div>

        <script>
            (adsbygoogle = window.adsbygoogle || []).push({{}});
            (adsbygoogle = window.adsbygoogle || []).push({{}});
        </script>
    </body>
    </html>
    """)

@app.route("/statistics")
def statistics():
    return render_template_string(f"""
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>Statistics - SureBet Pro</title>
        
        <!-- Google AdSense -->
        <script async src="https://pagead2.googlesyndication.com/pagead/js/adsbygoogle.js?client=ca-pub-6332657251575161"
            crossorigin="anonymous"></script>
        
        {BASE_STYLES}
    </head>
    <body>
        {NAVIGATION_TEMPLATE}
        
        <div class="container">
            <div class="main-content">
                <div class="hero-section">
                    <h1 class="hero-title">📊 Performance Statistics</h1>
                    <p class="hero-subtitle">Track our prediction accuracy and success rates</p>
                </div>

                <!-- Top Ad -->
                <div class="ad-container">
                    <div class="ad-label">Advertisement</div>
                    <ins class="adsbygoogle"
                        style="display:block"
                        data-ad-client="ca-pub-6332657251575161"
                        data-ad-slot="1509818329"
                        data-ad-format="auto"
                        data-full-width-responsive="true"></ins>
                </div>

                <div class="stats-container">
                    <div class="stat-card">
                        <span class="stat-number">87%</span>
                        <div class="stat-label">Overall Accuracy</div>
                    </div>
                    <div class="stat-card">
                        <span class="stat-number">156</span>
                        <div class="stat-label">Successful Predictions</div>
                    </div>
                    <div class="stat-card">
                        <span class="stat-number">2.4</span>
                        <div class="stat-label">Average Odds</div>
                    </div>
                    <div class="stat-card">
                        <span class="stat-number">30</span>
                        <div class="stat-label">Days Tracking</div>
                    </div>
                </div>

                <div class="card">
                    <h3>Monthly Performance</h3>
                    <p>Our prediction accuracy has been consistently above 85% for the past 3 months, with our highest success rate being 92% in May 2025.</p>
                </div>

                <!-- Bottom Ad -->
                <div class="ad-container">
                    <div class="ad-label">Advertisement</div>
                    <ins class="adsbygoogle"
                        style="display:block"
                        data-ad-client="ca-pub-6332657251575161"
                        data-ad-slot="1509818329"
                        data-ad-format="auto"
                        data-full-width-responsive="true"></ins>
                </div>
            </div>
        </div>

        <div class="footer">
            <div class="container">
                <p>&copy; 2025 SureBet Pro. All rights reserved. | Bet responsibly.</p>
            </div>
        </div>

        <script>
            (adsbygoogle = window.adsbygoogle || []).push({{}});
            (adsbygoogle = window.adsbygoogle || []).push({{}});
        </script>
    </body>
    </html>
    """)

@app.route("/about")
def about():
    return render_template_string(f"""
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>About Us - SureBet Pro</title>
        
        <!-- Google AdSense -->
        <script async src="https://pagead2.googlesyndication.com/pagead/js/adsbygoogle.js?client=ca-pub-6332657251575161"
            crossorigin="anonymous"></script>
        
        {BASE_STYLES}
    </head>
    <body>
        {NAVIGATION_TEMPLATE}
        
        <div class="container">
            <div class="main-content">
                <div class="hero-section">
                    <h1 class="hero-title">ℹ️ About SureBet Pro</h1>
                    <p class="hero-subtitle">Your trusted partner in professional betting predictions</p>
                </div>

                <!-- Top Ad -->
                <div class="ad-container">
                    <div class="ad-label">Advertisement</div>
                    <ins class="adsbygoogle"
                        style="display:block"
                        data-ad-client="ca-pub-6332657251575161"
                        data-ad-slot="1509818329"
                        data-ad-format="auto"
                        data-full-width-responsive="true"></ins>
                </div>

                <div class="card">
                    <h3>Our Mission</h3>
                    <p>At SureBet Pro, we combine advanced statistical analysis with expert football knowledge to provide you with the most accurate betting predictions. Our team of experienced analysts works around the clock to ensure you get the best possible insights for your betting decisions.</p>
                </div>

                <div class="card">
                    <h3>How We Work</h3>
                    <p>Our predictions are based on comprehensive data analysis including team form, head-to-head records, player statistics, weather conditions, and many other factors. We use machine learning algorithms to identify patterns and trends that give us an edge in prediction accuracy.</p>
                </div>

                <div class="card">
                    <h3>Responsible Gambling</h3>
                    <p>We promote responsible gambling and encourage our users to bet within their means. Gambling should be fun and entertaining, never a way to solve financial problems. Please gamble responsibly and seek help if you feel you have a gambling problem.</p>
                </div>

                <!-- Bottom Ad -->
                <div class="ad-container">
                    <div class="ad-label">Advertisement</div>
                    <ins class="adsbygoogle"
                        style="display:block"
                        data-ad-client="ca-pub-6332657251575161"
                        data-ad-slot="1509818329"
                        data-ad-format="auto"
                        data-full-width-responsive="true"></ins>
                </div>
            </div>
        </div>

        <div class="footer">
            <div class="container">
                <p>&copy; 2025 SureBet Pro. All rights reserved. | Bet responsibly.</p>
            </div>
        </div>

        <script>
            (adsbygoogle = window.adsbygoogle || []).push({{}});
            (adsbygoogle = window.adsbygoogle || []).push({{}});
        </script>
    </body>
    </html>
    """)

@app.route("/api/predictions")
def api_predictions():
    """API endpoint to get predictions as JSON"""
    return jsonify({
        "status": "success",
        "data": SAMPLE_PREDICTIONS,
        "last_updated": datetime.now().isoformat()
    })

@app.route("/api/statistics")
def api_statistics():
    """API endpoint to get statistics as JSON"""
    return jsonify({
        "status": "success",
        "data": {
            "overall_accuracy": 87,
            "successful_predictions": 156,
            "average_odds": 2.4,
            "tracking_days": 30,
            "monthly_performance": {
                "may_2025": 92,
                "april_2025": 89,
                "march_2025": 85
            }
        },
        "last_updated": datetime.now().isoformat()
    })

if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0", port=5000)

@app.route("/admin")
def admin():
    return render_template_string(f"""
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>Admin Panel - SureBet Pro</title>
        {BASE_STYLES}
    </head>
    <body>
        {NAVIGATION_TEMPLATE}
        <div class="container">
            <div class="main-content">
                <div class="card">
                    <h2>⚙️ Admin Panel</h2>
                    <p>This is a placeholder admin dashboard. Add controls and functionality here.</p>
                </div>
            </div>
        </div>
    </body>
    </html>
    """)
