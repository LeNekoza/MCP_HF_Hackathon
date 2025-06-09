# Analytics Integration Guide

## How to Integrate the Analytics System into the Main Gradio App

### 1. Update Main Interface

Modify `src/components/interface.py` to include the analytics dashboard:

```python
# Add this import at the top
from .analytics_interface import create_analytics_dashboard

# In the create_main_interface function, add this section:
# Replace the existing chart container with:

# Analytics Dashboard Section
analytics_dashboard, analysis_selector, chart_type_selector = create_analytics_dashboard()

# Add to the right column after the dashboard header:
with gr.Tab("Analytics") as analytics_tab:
    analytics_dashboard
```

### 2. Start Analytics API Server

Add this to `app.py` to run the analytics API alongside Gradio:

```python
import threading
from backend.api import app as analytics_app
import uvicorn

def start_analytics_api():
    """Start the analytics API server in a separate thread."""
    uvicorn.run(
        analytics_app,
        host="127.0.0.1", 
        port=8001,
        log_level="info"
    )

# In the main() function, add:
# Start analytics API in background
analytics_thread = threading.Thread(target=start_analytics_api, daemon=True)
analytics_thread.start()
```

### 3. Update Requirements

Ensure all analytics dependencies are installed:

```bash
source env/bin/activate
pip install -r requirements.txt
```

### 4. Test Integration

```bash
# Terminal 1: Start main app
source env/bin/activate
python app.py

# Terminal 2: Test analytics API
curl http://localhost:8001/analyses

# Terminal 3: Run analytics demo
python demo_analytics.py
```

### 5. Environment Variables

Ensure `.env` contains database configuration:

```env
# Database Configuration
NEON_HOST=your-neon-host
NEON_DATABASE=maindb
NEON_USER=your-user
NEON_PASSWORD=your-password
NEON_PORT=5432
NEON_SSLMODE=require

# Analytics API
API_PORT=8001
```

### 6. Navigation Integration

Update the navigation buttons to include analytics:

```html
<div class="nav-buttons-container">
    <button class="nav-btn active" data-section="dashboard">Dashboard</button>
    <button class="nav-btn" data-section="analytics">Analytics</button>
    <button class="nav-btn" data-section="alerts">Alerts</button>
    <button class="nav-btn" data-section="resources">Resources</button>
    <button class="nav-btn" data-section="data">Data</button>
</div>
```

### 7. CSS Styling

Add these CSS classes to the existing hospital CSS:

```css
.analytics-dashboard {
    padding: 20px;
    background: white;
    border-radius: 8px;
    margin: 10px;
}

.analytics-controls {
    margin-bottom: 20px;
    padding: 15px;
    background: #f8f9fa;
    border-radius: 8px;
}

.analysis-selector, .chart-type-selector {
    margin-right: 10px;
}

.summary-panel {
    background: #f1f5f9;
    padding: 15px;
    border-radius: 8px;
    border-left: 4px solid #3b82f6;
}

.metric {
    margin: 10px 0;
}

.metric-value {
    font-size: 1.5em;
    font-weight: bold;
    color: #1e40af;
}

.metric-label {
    color: #64748b;
    font-size: 0.9em;
}
```

### 8. Full Integration Example

Here's how the main interface would look with analytics integrated:

```python
def create_main_interface(config):
    with gr.Blocks(...) as demo:
        with gr.Row():
            # Left sidebar (existing)
            with gr.Column(scale=1):
                # ... existing chat interface
                
            # Right dashboard with analytics
            with gr.Column(scale=2):
                # Dashboard header
                # ... existing header
                
                # Navigation with analytics tab
                with gr.Tabs() as tabs:
                    with gr.Tab("Dashboard") as dash_tab:
                        # ... existing dashboard content
                        
                    with gr.Tab("Analytics") as analytics_tab:
                        analytics_dashboard, _, _ = create_analytics_dashboard()
                        
                    with gr.Tab("Alerts") as alerts_tab:
                        # ... existing alerts
    
    return demo
```

### 9. Real-time Updates

To enable real-time updates, add this JavaScript:

```javascript
// Auto-refresh analytics every 5 minutes
setInterval(function() {
    const refreshBtn = document.querySelector('.refresh-btn');
    if (refreshBtn && document.querySelector('.analytics-dashboard:visible')) {
        refreshBtn.click();
    }
}, 300000); // 5 minutes
```

### 10. Error Handling

The system automatically handles:
- ✅ Database connection failures (falls back to mock data)
- ✅ Missing database tables/columns  
- ✅ API endpoint errors
- ✅ Chart rendering errors
- ✅ Async operation timeouts

### 11. Deployment Checklist

Before deploying:

- [ ] Database credentials configured in `.env`
- [ ] All dependencies installed (`pip install -r requirements.txt`)
- [ ] Analytics API port (8001) available
- [ ] Mock data fallback tested
- [ ] All test cases passing (`python test_analytics.py`)
- [ ] Demo script working (`python demo_analytics.py`)

### 12. Monitoring

Monitor the analytics system with:

```bash
# Check API health
curl http://localhost:8001/

# View analytics logs
tail -f logs/analytics.log

# Test individual analysis
curl http://localhost:8001/analysis/admission_split
```

The analytics system is now ready for production use with comprehensive error handling, fallback systems, and integration with the existing Gradio dashboard. 