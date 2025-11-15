# backend.py - COMPLETE VERSION with comprehensive chart generation
from flask import Flask, request, jsonify, render_template, send_file
from flask_cors import CORS
from app import get_prediction, RIPENESS_CLASSES, FRUIT_TYPES
from PIL import Image
import os
import pandas as pd
from datetime import datetime
import re
import io
import numpy as np

# Serial communication for IoT
try:
    import serial
    SERIAL_AVAILABLE = True
except:
    SERIAL_AVAILABLE = False

# Plotly for chart generation
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import plotly.utils
import json

# Frontend path configuration
frontend_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'frontend')

app = Flask(__name__, 
            template_folder=frontend_path,
            static_folder=frontend_path,
            static_url_path='')

CORS(app)

# CSV configuration
CSV_FILE = 'fruit_analysis_results.csv'
result_counter = 0

# Initialize CSV
if os.path.exists(CSV_FILE):
    df = pd.read_csv(CSV_FILE)
    result_counter = len(df)
else:
    df = pd.DataFrame(columns=[
        'ID', 'Timestamp', 'Date', 'Time', 'Source', 'Is_Fruit',
        'Fruit_Type', 'Fruit_Confidence', 'Ripeness', 'Ripeness_Confidence',
        'Temperature_C', 'Humidity_pct', 'Shelf_Life'
    ])
    df.to_csv(CSV_FILE, index=False)

# ==================== ROUTES ==================== #

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/preview.html')
def preview():
    return render_template('preview.html')

@app.route('/result.html')
def result():
    return render_template('result.html')

@app.route('/dashboard.html')
def dashboard():
    return render_template('dashboard.html')

@app.route('/history.html')
def history():
    return render_template('history.html')

# ==================== PREDICTION ==================== #

@app.route('/predict', methods=['POST'])
def predict():
    global result_counter
    
    if 'image' not in request.files:
        return jsonify({'error': 'No image uploaded'}), 400
    
    file = request.files['image']
    img = Image.open(file.stream)
    result = get_prediction(img)
    
    # Save to CSV
    result_counter += 1
    timestamp = datetime.now()
    
    entry = {
        'ID': result_counter,
        'Timestamp': timestamp.strftime("%Y-%m-%d %H:%M:%S"),
        'Date': timestamp.strftime("%Y-%m-%d"),
        'Time': timestamp.strftime("%H:%M:%S"),
        'Source': 'Camera/Upload',
        'Is_Fruit': result.get('is_fruit', True),
        'Fruit_Type': result.get('fruit', 'N/A'),
        'Fruit_Confidence': round(result.get('fruit_conf', 0) * 100, 2),
        'Ripeness': result.get('ripeness', 'N/A'),
        'Ripeness_Confidence': round(result.get('ripeness_conf', 0) * 100, 2),
        'Temperature_C': None,
        'Humidity_pct': None,
        'Shelf_Life': None
    }
    
    df = pd.read_csv(CSV_FILE)
    df = pd.concat([df, pd.DataFrame([entry])], ignore_index=True)
    df.to_csv(CSV_FILE, index=False)
    
    result['result_id'] = result_counter
    
    return jsonify(result)

# ==================== IOT SENSOR ==================== #

@app.route('/read_sensor', methods=['POST'])
def read_sensor():
    if not SERIAL_AVAILABLE:
        return jsonify({'error': 'PySerial not installed'}), 500
    
    try:
        esp = serial.Serial('COM5', 115200, timeout=2)
        import time
        time.sleep(1.5)
        
        temp, hum = None, None
        for _ in range(40):
            raw = esp.readline().decode('ascii', errors='ignore').strip()
            if not raw:
                continue
            low = raw.lower()
            if low.startswith('ets') or 'boot' in low:
                continue
            if 'humidity' in low and 'temperature' in low:
                temp, hum = parse_temp_hum(raw)
                break
        
        esp.close()
        
        if temp is None or hum is None:
            return jsonify({'error': 'No valid sensor data'}), 400
        
        return jsonify({'temperature': temp, 'humidity': hum})
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500

def parse_temp_hum(line):
    try:
        clean = line.replace('°', ' ').replace('%', ' ').replace('C', ' ').replace('c', ' ')
        clean = clean.replace(',', ' ')
        hum_m = re.search(r'humidity[:=\s]+([+-]?\d*\.?\d+)', clean, re.IGNORECASE)
        temp_m = re.search(r'temperature[:=\s]+([+-]?\d*\.?\d+)', clean, re.IGNORECASE)
        
        hum = float(hum_m.group(1)) if hum_m else None
        temp = float(temp_m.group(1)) if temp_m else None
        
        if hum and (hum < 0 or hum > 100):
            hum = None
        if temp and (temp < -20 or temp > 60):
            temp = None
        
        return temp, hum
    except:
        return None, None

# ==================== UPDATE RESULT ==================== #

@app.route('/update_result', methods=['POST'])
def update_result():
    data = request.json
    result_id = data.get('result_id')
    temp = data.get('temperature')
    hum = data.get('humidity')
    shelf_life = data.get('shelf_life')
    
    df = pd.read_csv(CSV_FILE)
    df.loc[df['ID'] == result_id, 'Temperature_C'] = temp
    df.loc[df['ID'] == result_id, 'Humidity_pct'] = hum
    df.loc[df['ID'] == result_id, 'Shelf_Life'] = shelf_life
    df.loc[df['ID'] == result_id, 'Source'] = 'Combined(IoT)'
    df.to_csv(CSV_FILE, index=False)
    
    return jsonify({'success': True})

# ==================== DASHBOARD DATA ==================== #

@app.route('/dashboard_data', methods=['GET'])
def dashboard_data():
    try:
        df = pd.read_csv(CSV_FILE)
        
        if len(df) == 0:
            return jsonify({'error': 'No data available'}), 404
        
        # Prepare data
        df['Date'] = pd.to_datetime(df['Date'], errors='coerce')
        df_iot = df[(df['Temperature_C'].notna()) & (df['Humidity_pct'].notna())]
        
        # ✅ FIX: Handle NaN, bool, and numpy types
        def clean_for_json(value):
            # Handle NaN
            if pd.isna(value):
                return None
            if isinstance(value, float) and value != value:  # NaN check
                return None
            # ✅ Handle boolean (THIS WAS MISSING!)
            if isinstance(value, (bool, np.bool_)):
                return bool(value)
            # Handle numpy numbers
            if isinstance(value, (np.floating, np.integer)):
                return float(value)
            # Handle numpy strings
            if isinstance(value, np.str_):
                return str(value)
            return value
        
        # Generate all charts
        charts = {}
        
        # ========== CORE ANALYTICS CHARTS (Always show) ==========
        
        # 1. Fruit distribution
        fruit_counts = df['Fruit_Type'].value_counts()
        fig_fruit = px.pie(values=fruit_counts.values, names=fruit_counts.index,
                          title="Fruit Type Distribution")
        charts['fruitDistribution'] = json.loads(json.dumps(fig_fruit, cls=plotly.utils.PlotlyJSONEncoder))
        
        # 2. Ripeness distribution
        ripeness_counts = df['Ripeness'].value_counts()
        color_map = {'Unripe': '#90EE90', 'Ripe': '#FFD700', 'Overripe': '#FF6347', 'Not Fruit': '#808080'}
        fig_ripeness = px.pie(values=ripeness_counts.values, names=ripeness_counts.index,
                             title="Ripeness Distribution",
                             color_discrete_map=color_map)
        charts['ripenessDistribution'] = json.loads(json.dumps(fig_ripeness, cls=plotly.utils.PlotlyJSONEncoder))
        
        # 3. Confidence scatter
        fig_scatter = px.scatter(df, x='Fruit_Confidence', y='Ripeness_Confidence',
                                color='Ripeness', size='Fruit_Confidence',
                                hover_data=['Fruit_Type', 'Source'],
                                title="Fruit vs Ripeness Confidence",
                                color_discrete_map=color_map)
        charts['confidenceScatter'] = json.loads(json.dumps(fig_scatter, cls=plotly.utils.PlotlyJSONEncoder))
        
        # 4. Source distribution
        source_counts = df['Source'].value_counts()
        fig_source = px.pie(values=source_counts.values, names=source_counts.index,
                           hole=0.5, title="Data Source Breakdown")
        charts['sourceDistribution'] = json.loads(json.dumps(fig_source, cls=plotly.utils.PlotlyJSONEncoder))
        
        # 5. Stacked bar
        fruit_ripeness = df.groupby(['Fruit_Type', 'Ripeness']).size().reset_index(name='Count')
        fig_stacked = px.bar(fruit_ripeness, x='Fruit_Type', y='Count', color='Ripeness',
                            title="Fruit Type by Ripeness Level", barmode='stack',
                            color_discrete_map=color_map)
        charts['stackedBar'] = json.loads(json.dumps(fig_stacked, cls=plotly.utils.PlotlyJSONEncoder))
        
        # 6. Grouped bar
        fig_grouped = px.bar(fruit_ripeness, x='Fruit_Type', y='Count', color='Ripeness',
                            title="Fruit Type by Ripeness (Grouped)", barmode='group',
                            color_discrete_map=color_map)
        charts['groupedBar'] = json.loads(json.dumps(fig_grouped, cls=plotly.utils.PlotlyJSONEncoder))
        
        # 7. Box plots
        fig_box_fruit = px.box(df, x='Fruit_Type', y='Fruit_Confidence',
                              title="Fruit Confidence Distribution",
                              color='Fruit_Type', points="all")
        charts['fruitConfBox'] = json.loads(json.dumps(fig_box_fruit, cls=plotly.utils.PlotlyJSONEncoder))
        
        fig_box_ripeness = px.box(df, x='Ripeness', y='Ripeness_Confidence',
                                 title="Ripeness Confidence Distribution",
                                 color='Ripeness', points="all",
                                 color_discrete_map=color_map)
        charts['ripenessConfBox'] = json.loads(json.dumps(fig_box_ripeness, cls=plotly.utils.PlotlyJSONEncoder))
        
        # ========== ENVIRONMENTAL CHARTS (Only if IoT data exists) ==========
        if len(df_iot) > 0:
            # 1. Temperature & Humidity combined timeline
            fig_combined = make_subplots(
                rows=2, cols=1,
                subplot_titles=("Temperature (°C)", "Humidity (%)"),
                vertical_spacing=0.12,
                shared_xaxes=True
            )
            
            fig_combined.add_trace(
                go.Scatter(x=df_iot['Timestamp'], y=df_iot['Temperature_C'],
                          mode='lines+markers', name='Temperature',
                          line=dict(color='#FF6347', width=2), marker=dict(size=8)),
                row=1, col=1
            )
            
            fig_combined.add_trace(
                go.Scatter(x=df_iot['Timestamp'], y=df_iot['Humidity_pct'],
                          mode='lines+markers', name='Humidity',
                          line=dict(color='#4682B4', width=2), marker=dict(size=8)),
                row=2, col=1
            )
            
            fig_combined.update_layout(height=600, showlegend=False)
            charts['tempHumCombined'] = json.loads(json.dumps(fig_combined, cls=plotly.utils.PlotlyJSONEncoder))
            
            # 2. Temperature Distribution
            fig_temp_hist = px.histogram(df_iot, x='Temperature_C', nbins=20,
                                         title="Temperature Distribution",
                                         color_discrete_sequence=['#FF6347'])
            fig_temp_hist.update_layout(xaxis_title="Temperature (°C)", yaxis_title="Frequency")
            charts['tempDistribution'] = json.loads(json.dumps(fig_temp_hist, cls=plotly.utils.PlotlyJSONEncoder))
            
            # 3. Humidity Distribution
            fig_hum_hist = px.histogram(df_iot, x='Humidity_pct', nbins=20,
                                       title="Humidity Distribution",
                                       color_discrete_sequence=['#4682B4'])
            fig_hum_hist.update_layout(xaxis_title="Humidity (%)", yaxis_title="Frequency")
            charts['humDistribution'] = json.loads(json.dumps(fig_hum_hist, cls=plotly.utils.PlotlyJSONEncoder))
            
            # 4. Temperature vs Humidity Correlation
            fig_correlation = px.scatter(df_iot, x='Temperature_C', y='Humidity_pct',
                                        color='Ripeness', size='Fruit_Confidence',
                                        hover_data=['Fruit_Type', 'Timestamp'],
                                        title="Temperature vs Humidity by Ripeness",
                                        color_discrete_map=color_map)
            charts['tempHumCorrelation'] = json.loads(json.dumps(fig_correlation, cls=plotly.utils.PlotlyJSONEncoder))
            
            # 5. Box plots by category
            fig_temp_fruit = px.box(df_iot, x='Fruit_Type', y='Temperature_C',
                                   color='Fruit_Type', title="Temperature by Fruit Type", points="all")
            charts['tempByFruit'] = json.loads(json.dumps(fig_temp_fruit, cls=plotly.utils.PlotlyJSONEncoder))
            
            fig_temp_ripeness = px.box(df_iot, x='Ripeness', y='Temperature_C',
                                       color='Ripeness', title="Temperature by Ripeness",
                                       color_discrete_map=color_map, points="all")
            charts['tempByRipeness'] = json.loads(json.dumps(fig_temp_ripeness, cls=plotly.utils.PlotlyJSONEncoder))
            
            fig_hum_fruit = px.box(df_iot, x='Fruit_Type', y='Humidity_pct',
                                  color='Fruit_Type', title="Humidity by Fruit Type", points="all")
            charts['humByFruit'] = json.loads(json.dumps(fig_hum_fruit, cls=plotly.utils.PlotlyJSONEncoder))
            
            fig_hum_ripeness = px.box(df_iot, x='Ripeness', y='Humidity_pct',
                                     color='Ripeness', title="Humidity by Ripeness",
                                     color_discrete_map=color_map, points="all")
            charts['humByRipeness'] = json.loads(json.dumps(fig_hum_ripeness, cls=plotly.utils.PlotlyJSONEncoder))
            
            # 6. Heatmaps
            temp_pivot = df_iot.pivot_table(values='Temperature_C', index='Ripeness',
                                           columns='Fruit_Type', aggfunc='mean')
            fig_heat_temp = px.imshow(temp_pivot, text_auto='.1f',
                                     title="Average Temperature by Category",
                                     color_continuous_scale='Reds',
                                     labels=dict(color="Temp (°C)"))
            charts['tempHeatmap'] = json.loads(json.dumps(fig_heat_temp, cls=plotly.utils.PlotlyJSONEncoder))
            
            hum_pivot = df_iot.pivot_table(values='Humidity_pct', index='Ripeness',
                                          columns='Fruit_Type', aggfunc='mean')
            fig_heat_hum = px.imshow(hum_pivot, text_auto='.1f',
                                    title="Average Humidity by Category",
                                    color_continuous_scale='Blues',
                                    labels=dict(color="Humidity (%)"))
            charts['humHeatmap'] = json.loads(json.dumps(fig_heat_hum, cls=plotly.utils.PlotlyJSONEncoder))
            
            # 7. Gauges
            avg_temp = df_iot['Temperature_C'].mean()
            avg_hum = df_iot['Humidity_pct'].mean()
            
            fig_gauge_temp = go.Figure(go.Indicator(
                mode="gauge+number", value=avg_temp,
                title={'text': "Average Temperature"},
                gauge={'axis': {'range': [0, 40]},
                      'bar': {'color': "#FF6347"},
                      'steps': [
                          {'range': [0, 10], 'color': "#ADD8E6"},
                          {'range': [10, 20], 'color': "#90EE90"},
                          {'range': [20, 30], 'color': "#FFD700"},
                          {'range': [30, 40], 'color': "#FF6347"}
                      ]}
            ))
            fig_gauge_temp.update_layout(height=300)
            charts['tempGauge'] = json.loads(json.dumps(fig_gauge_temp, cls=plotly.utils.PlotlyJSONEncoder))
            
            fig_gauge_hum = go.Figure(go.Indicator(
                mode="gauge+number", value=avg_hum,
                title={'text': "Average Humidity"},
                gauge={'axis': {'range': [0, 100]},
                      'bar': {'color': "#4682B4"},
                      'steps': [
                          {'range': [0, 30], 'color': "#FFE4B5"},
                          {'range': [30, 50], 'color': "#ADD8E6"},
                          {'range': [50, 70], 'color': "#90EE90"},
                          {'range': [70, 100], 'color': "#4682B4"}
                      ]}
            ))
            fig_gauge_hum.update_layout(height=300)
            charts['humGauge'] = json.loads(json.dumps(fig_gauge_hum, cls=plotly.utils.PlotlyJSONEncoder))
            
            # Environmental stats
            charts['stats'] = {
                'minTemp': round(df_iot['Temperature_C'].min(), 1),
                'maxTemp': round(df_iot['Temperature_C'].max(), 1),
                'avgTemp': round(avg_temp, 1),
                'minHum': round(df_iot['Humidity_pct'].min(), 1),
                'maxHum': round(df_iot['Humidity_pct'].max(), 1),
                'avgHum': round(avg_hum, 1),
                'correlation': float(df_iot['Temperature_C'].corr(df_iot['Humidity_pct']))
            }
            
            # Quality status
            charts['qualityStatus'] = {
                'optimal': bool(20 <= avg_temp <= 25 and 50 <= avg_hum <= 70),  # ✅ Convert to bool
                'acceptable': bool(15 <= avg_temp <= 30 and 40 <= avg_hum <= 80),  # ✅ Convert to bool
            }
        
        # ========== METRICS (Clean NaN values) ==========
        avg_temp = df['Temperature_C'].dropna().mean()
        avg_hum = df['Humidity_pct'].dropna().mean()
        
        metrics = {
            'total_analyses': int(len(df)),
            'avg_fruit_conf': clean_for_json(df['Fruit_Confidence'].mean()),
            'avg_ripeness_conf': clean_for_json(df['Ripeness_Confidence'].mean()),
            'most_common_fruit': str(df['Fruit_Type'].mode()[0]) if len(df) > 0 else 'N/A',
            'avg_temp': clean_for_json(avg_temp),
            'avg_humidity': clean_for_json(avg_hum)
        }
        
        # ========== INSIGHTS ==========
        insights = []
        if len(df) > 0:
            insights.append(f"Most frequently analyzed fruit: **{metrics['most_common_fruit']}**")
        
        if len(df['Ripeness'].unique()) > 1:
            top_ripeness = df['Ripeness'].value_counts().index[0]
            insights.append(f"Most common ripeness: **{top_ripeness}**")
        
        low_conf = df[df['Fruit_Confidence'] < 50]
        if len(low_conf) > 0:
            insights.append("⚠️ Some analyses have low confidence. Check lighting.")
        
        if len(source_counts) > 0:
            insights.append(f"Most used source: **{source_counts.index[0]}**")
        
        # ✅ Clean raw data for JSON (Handle ALL types including bool)
        raw_data_cleaned = []
        for record in df.to_dict('records'):
            cleaned_record = {}
            for key, value in record.items():
                cleaned_record[key] = clean_for_json(value)
            raw_data_cleaned.append(cleaned_record)
        
        print(f"✅ Dashboard generated: {len(charts)} charts, {len(df)} records")
        
        return jsonify({
            'charts': charts,
            'metrics': metrics,
            'insights': insights,
            'rawData': raw_data_cleaned
        })
        
    except Exception as e:
        print(f"❌ Dashboard error: {str(e)}")
        import traceback
        traceback.print_exc()
        return jsonify({'error': str(e)}), 500


# ==================== HISTORY DATA ==================== #

@app.route('/history_data', methods=['GET'])
def history_data():
    try:
        df = pd.read_csv(CSV_FILE)
        
        # ✅ Clean NaN values for JSON serialization
        def clean_for_json(value):
            if pd.isna(value) or (isinstance(value, float) and value != value):  # Check for NaN
                return None
            if isinstance(value, (np.floating, np.integer)):
                return float(value)
            if isinstance(value, np.bool_):
                return bool(value)
            return value
        
        # Convert to dict and clean all values
        records = df.to_dict('records')
        cleaned_records = []
        
        for record in records:
            cleaned_record = {}
            for key, value in record.items():
                cleaned_record[key] = clean_for_json(value)
            cleaned_records.append(cleaned_record)
        
        return jsonify(cleaned_records)
        
    except Exception as e:
        print(f"❌ History error: {str(e)}")
        import traceback
        traceback.print_exc()
        return jsonify({'error': str(e)}), 500


# ==================== DOWNLOAD CSV ==================== #

@app.route('/download_csv', methods=['GET'])
def download_csv():
    return send_file(CSV_FILE, as_attachment=True, 
                     download_name=f'fruit_analysis_{datetime.now().strftime("%Y%m%d_%H%M%S")}.csv')

# ==================== RUN ==================== #

if __name__ == "__main__":
    app.run(port=5000, debug=True)
