📊 AI-Based E-Commerce Analytics System
🚀 Overview
This project is a real-time e-commerce analytics system that collects, processes, and visualizes user activity data to generate actionable business insights.
Instead of using Kafka, we built a custom REST API pipeline to simulate and handle streaming data efficiently.
The system enables monitoring of user behavior, sales trends, and performance metrics through interactive dashboards.
🎯 Objectives
Collect real-time user interaction data
Analyze purchasing patterns and trends
Provide live dashboards for decision-making
Implement ML models for predictions
🏗️ System Architecture
Copy code

User Activity → API (Data Collection) → Processing Layer → Database → Dashboard
⚙️ Tech Stack
🔹 Frontend
HTML, CSS, JavaScript
Dashboard visualization
🔹 Backend
Python (Flask/FastAPI) OR Node.js (based on your implementation)
REST APIs for data ingestion
🔹 Data Processing
Batch / Near real-time processing logic
🔹 Database
InfluxDB / MySQL / MongoDB
🔹 Visualization
Grafana (for dashboards)
🔹 Machine Learning
Linear Regression
K-Nearest Neighbors (KNN)
🔄 Workflow
Data Collection
User actions (clicks, views, purchases) are sent via API
Data Processing
Data is cleaned and structured
Storage
Stored in database for analysis
Analytics
ML models process data to generate insights
Visualization
Grafana dashboards display real-time metrics
📊 Features
✅ Real-time data collection using APIs
✅ Live analytics dashboard
✅ User behavior tracking
✅ Sales trend analysis
✅ Predictive analytics using ML models
✅ Scalable and modular design
🤖 Machine Learning Models
1. Linear Regression
Used for predicting sales trends
Helps in forecasting revenue
2. K-Nearest Neighbors (KNN)
Used for user behavior analysis
Helps in recommendation logic
📈 Results
Improved processing speed (near real-time)
Efficient handling of multiple user requests
Accurate trend prediction using ML models
Clear visualization of key metrics
🔮 Future Enhancements
Integration with Kafka for large-scale streaming
Advanced ML models (Deep Learning)
Real-time recommendation system
Cloud deployment (AWS/GCP)
User segmentation and personalization
📂 Project Structure
Copy code

/frontend        → UI files
/backend         → API and server logic
/models          → ML models
/database        → DB configuration
/dashboard       → Grafana setup
🛠️ How to Run
Clone the repository
Copy code

git clone <your-repo-link>
Install dependencies
Copy code

pip install -r requirements.txt
Run backend server
Copy code

python app.py
Start frontend
Copy code

npm start / open index.html
Open Grafana dashboard

Conclusion
This project demonstrates how API-based streaming systems can effectively replace traditional streaming tools for smaller-scale applications while still delivering real-time analytics and intelligent insights.