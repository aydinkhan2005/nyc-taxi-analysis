# NYC Taxi Capstone Project Plan
## MAST30034 Applied Data Science

**Research Question:**
> Which pickup zones have underperformed financially over time for our drivers, and what external factors explain this underperformance? How should vendors strategically respond?

**Timeline:** Jan-Jun 2019 (6 months, sequential)  
**Target Audience:** Fleet managers / taxi vendors  
**Taxi Type:** Yellow taxis  
**Key Metric:** Revenue per minute (primary)

---

## PHASE 1: DATA SOURCING & SETUP (Week 1)

### 1.1 NYC Taxi Data
- [ ] Download TLC yellow taxi data for Jan-Jun 2019 from https://www.nyc.gov/site/tlc/about/tlc-trip-record-data.html
  - Format: Parquet files (6 files, one per month)
  - Expected size: ~8-10GB total (manageable with PySpark)
- [ ] Download TLC zone shapefile (.shp, .shx, .dbf files)
- [ ] Review TLC data dictionary (check field definitions, missing value codes)
- [ ] Verify data includes zone names (not just coordinates)

### 1.2 Set Up Development Environment
- [ ] Create virtual environment (Python 3.8+)
- [ ] Install requirements:
  - PySpark (2.4.5 or later)
  - GeoPandas (for spatial analysis)
  - Pandas, NumPy, Scikit-learn
  - Matplotlib, Seaborn (visualization)
  - Folium (interactive maps, optional)
  - Requests (for API calls)
- [ ] Create requirements.txt
- [ ] Test PySpark installation (can you create a simple DataFrame?)

### 1.3 GitHub Setup
- [ ] Accept GitHub Classroom assignment
- [ ] Clone template repository
- [ ] Create initial folder structure:
  ```
  repo/
  ├── README.md
  ├── requirements.txt
  ├── data/
  │   ├── raw/  (TLC parquet files)
  │   ├── processed/  (cleaned data)
  │   └── external/  (weather, events, etc.)
  ├── notebooks/
  │   ├── 01_data_loading.ipynb
  │   ├── 02_eda.ipynb
  │   ├── 03_external_data.ipynb
  │   ├── 04_analysis.ipynb
  │   └── 05_modeling.ipynb
  ├── src/
  │   ├── preprocessing.py
  │   ├── analysis.py
  │   └── modeling.py
  └── output/
      └── figures/  (for report)
  ```
- [ ] Make first commit: "Initial setup"

---

## PHASE 2: EXPLORATORY DATA ANALYSIS (Week 1-2)

### 2.1 Load & Inspect Data
**Notebook: `01_data_loading.ipynb`**

- [ ] Load one month of TLC data into PySpark
- [ ] Check schema (columns, data types)
- [ ] Inspect first few rows
- [ ] Check row counts per month
- [ ] Document any data quality issues (nulls, outliers)

**Questions to answer:**
- How many trips per month?
- Data coverage (all zones? all days?)
- Any obvious data quality issues?

### 2.2 Exploratory Data Analysis
**Notebook: `02_eda.ipynb`**

**Basic Statistics:**
- [ ] Total trips per zone (across all 6 months)
- [ ] Revenue per zone (total_amount)
- [ ] Average trip distance, duration, fare per zone
- [ ] Passenger count distribution
- [ ] Payment method breakdown
- [ ] Tip distribution (amount and % of fare)

**Time-Based Analysis:**
- [ ] Trips by day of week
- [ ] Trips by hour of day
- [ ] Trips by month (see any trends?)
- [ ] Weekday vs. weekend patterns

**Geospatial:**
- [ ] Load shapefile into GeoPandas
- [ ] Plot all zones (visualize NYC geography)
- [ ] Identify zone clusters (geographic regions)
- [ ] Count zones per region

**Key Metric Calculation:**
- [ ] Calculate revenue per minute for each zone
  ```
  revenue_per_minute = total_amount / (trip_duration_minutes)
  ```
- [ ] Aggregate by zone (mean, median, std)
- [ ] Identify top 10 and bottom 10 zones by revenue per minute
- [ ] Create summary table (Table 1 for report)

**Questions to answer:**
- Which zones have highest/lowest revenue per minute?
- Are there clear geographic clusters?
- Do revenue patterns vary by time-of-day/day-of-week?
- Any obvious outliers or data quality issues?

### 2.3 Data Cleaning & Preprocessing
**Notebook & Code: `src/preprocessing.py`**

**Decisions to document:**
- [ ] Outlier handling: Define and remove unreasonable values
  - Trip duration: Remove trips < 1 minute or > 24 hours (with justification from TLC dictionary)
  - Fare amount: Remove negative fares or extreme outliers (>$500)
  - Revenue per minute: Remove zones with < 100 trips (insufficient sample)
- [ ] Missing values: Check for nulls in key columns
  - tpep_pickup_datetime, pickup_locationid, total_amount, trip_distance
  - Document any rows removed and % of data lost
- [ ] Data filtering decisions: 
  - Only include trips with valid zone IDs (match shapefile)
  - Only include zones present in shapefile (drop unmapped zones if any)

**Create clean dataset:**
- [ ] Save processed data (Parquet format, one file per month)
- [ ] Document shape at each step (input rows → output rows)
- [ ] Track % of data retained

---

## PHASE 3: DEFINE UNDERPERFORMANCE METRIC (Week 2)

### 3.1 Neighbor-Based Underperformance
**Notebook: `02_eda.ipynb` (continued) & Code: `src/analysis.py`**

**Goal:** Define which zones underperform relative to geographic neighbors

**Implementation:**
- [ ] For each zone, identify geographic neighbors (touching zones)
  ```python
  neighbors = zones_gdf[zones_gdf.geometry.touches(zone_geometry)]
  ```
- [ ] Calculate mean revenue per minute for each zone's neighbors
- [ ] Calculate underperformance metric:
  ```
  underperformance_pct = ((neighbor_mean - zone_mean) / neighbor_mean) * 100
  ```
- [ ] Flag zones underperforming by >10% (or define threshold)

**Document assumptions:**
- [ ] Write clearly: "We assume neighboring zones have similar demand characteristics"
- [ ] Note edge cases: zones with few/no neighbors
- [ ] Fallback for edge cases (compare to region average or citywide average)

**Deliverables:**
- [ ] Table: Zone name, revenue_per_minute, neighbor_mean, underperformance_pct
- [ ] Visualization: Map showing underperformance by zone (choropleth)
- [ ] Identify 5-10 target zones for deep analysis

**Questions to answer:**
- Which zones are most underperforming vs. neighbors?
- Are they clustered geographically or scattered?
- Are they in high-potential areas (downtown, midtown) or peripheral?

### 3.2 Temporal Underperformance (Decline Over Time)
**Notebook: `02_eda.ipynb` (continued) & Code: `src/analysis.py`**

**Goal:** Identify zones with declining revenue trends

**Implementation:**
- [ ] Calculate monthly revenue per zone for each month (Jan-Jun)
  ```python
  monthly_revenue = df.groupby(['month', 'pickup_zone'])['revenue_per_minute'].mean()
  ```
- [ ] For each zone, fit linear trend (6 months of data)
  ```python
  slope = np.polyfit(months_numeric, revenue_values, 1)[0]
  ```
- [ ] Flag zones with negative slope (declining)
- [ ] Calculate % decline from Jan to Jun

**Deliverables:**
- [ ] Time-series plot: Top 5 decliners (revenue per month)
- [ ] Slope distribution: Histogram of all zones' trends
- [ ] Table: Zone name, Jan revenue, Jun revenue, slope, % decline

**Questions to answer:**
- Which zones show steepest decline?
- Is the decline consistent month-to-month or sudden?
- Do decliners overlap with neighbor-based underperformers?

### 3.3 Combined Analysis
- [ ] Identify overlap: Zones that are BOTH underperforming neighbors AND declining
- [ ] Create final target list: 5-10 zones for investigation
- [ ] Prioritize by:
  - Magnitude of underperformance
  - Steepness of decline (if applicable)
  - Geographic interest (clustered or scattered)

---

## PHASE 4: EXTERNAL DATA SOURCING (Week 2)

### 4.1 Weather Data
**Source:** NOAA or OpenWeatherMap API

- [ ] Obtain daily weather for NYC (Jan-Jun 2019):
  - Average temperature
  - Precipitation (inches/mm)
  - Wind speed
  - Cloud cover
  - Weather condition (sunny, rainy, snow, etc.)
- [ ] Merge with taxi data by date
- [ ] Aggregate to monthly level (mean temp, total precipitation, etc.)

**Deliverables:**
- [ ] CSV file: Date, temp, precip, wind, condition
- [ ] Merged with taxi data by month

**Justification for report:**
- "Weather directly impacts taxi demand. Rainy/snowy days see fewer trips; temperature affects demand for rides."

### 4.2 NYC Events & Holidays
**Sources:** Manual curation + NYC event calendars

- [ ] Identify major events/holidays in Jan-Jun 2019:
  - National holidays (New Year's Day, Presidents' Day, Memorial Day)
  - Local events (NYC Marathon in Nov? Doesn't apply to Jan-Jun, check what's relevant)
  - Major concerts, sports events (check if any major events in timeframe)
  - School holidays (check NYC public school calendar)

- [ ] Create binary indicators or event count per month

**Deliverables:**
- [ ] Table: Date, holiday/event name, type (holiday/concert/sports/etc.)
- [ ] Monthly summary: Count of events per month

**Justification for report:**
- "Major events and holidays influence taxi demand patterns. Events attract visitors and increase trip volume; holidays may reduce commuter trips."

### 4.3 NYC Zone Characteristics (Optional but Impressive)
**Sources:** Google Maps API, NYC Open Data, manual research

- [ ] For your target zones, document:
  - Nearby attractions (subway stations, parks, landmarks)
  - Zone type (business district, residential, airport, tourist)
  - Commercial vs. residential density
  - Distance to major hubs (airports, Times Square, Central Park)

**Deliverables:**
- [ ] Descriptive table: Zone name, type, nearby attractions, characteristics
- [ ] This will support recommendations

**Why:** "Context helps explain why a zone underperforms—maybe it's in a changing neighborhood or has poor accessibility."

---

## PHASE 5: ANALYSIS & VISUALIZATION (Week 3)

### 5.1 Underperformance Analysis
**Notebook: `04_analysis.ipynb` & Code: `src/analysis.py`**

**For each target zone, investigate:**

1. **Revenue Pattern Over Time**
   - [ ] Plot monthly revenue (Jan-Jun) with trend line
   - [ ] Compare to city average and neighbor average
   - [ ] Identify if decline is smooth or abrupt

2. **Temporal Patterns**
   - [ ] Day-of-week revenue (does this zone show different patterns?)
   - [ ] Hour-of-day revenue (peak hours?)
   - [ ] Weekday vs. weekend behavior

3. **External Factors Alignment**
   - [ ] Overlay weather on revenue trend
     - Does precipitation correlate with revenue drops?
     - Does temperature affect the zone differently than others?
   - [ ] Overlay events/holidays
     - Do major events cause spikes?
   - [ ] Check for anomalies: "Revenue dropped in April—what happened then?"

4. **Comparative Analysis**
   - [ ] Compare each underperformer to its best-performing neighbor
   - [ ] What's different? (accessibility, nearby attractions, land use?)
   - [ ] Are neighboring zones also affected by same external factors?

**Deliverables (for report):**
- [ ] Figure 1-2: Revenue trends for 3-5 target zones with external factors overlay
- [ ] Figure 3: Time-of-day patterns for underperformers vs. neighbors
- [ ] Figure 4: Geospatial map showing underperforming zones + neighbors
- [ ] Tables: Summary statistics for target zones

**Analysis narrative:**
> "From Figure X, we observe that Zone Q's revenue declined from $X/min (Jan) to $Y/min (Jun). This decline aligns with [external factor]. In contrast, neighboring Zone R remained stable, suggesting [interpretation]."

### 5.2 Distribution & Outlier Analysis
**Notebook: `04_analysis.ipynb` & Code: `src/analysis.py`**

- [ ] Revenue per minute distribution (per zone)
  - Identify outliers (trips with unusually high/low revenue)
  - Remove or flag extreme outliers (>3 std deviations)
- [ ] Summarize findings:
  - Which zones have highest variance in revenue?
  - Which zones are most stable?

**Deliverable:**
- [ ] Box plot or violin plot: Revenue distribution by zone (top 10 zones)

---

## PHASE 6: STATISTICAL MODELING (Week 3-4)

### 6.1 Model 1: Linear Regression
**Predicting Revenue Per Minute**

**Setup:**
- [ ] Define target variable: `revenue_per_minute`
- [ ] Define input features:
  - Zone ID
  - Month (1-6)
  - Day of week (0-6)
  - Hour of day (0-23)
  - Average temperature (that month)
  - Precipitation (that month)
  - Event count (that month)
  - Any zone characteristics (distance to airport, etc., if using)

**Implementation:**
```python
from sklearn.linear_model import LinearRegression
from sklearn.preprocessing import StandardScaler
from sklearn.model_selection import train_test_split

# Split: Jan-Apr for training, May-Jun for testing
X_train = features_jan_apr
y_train = revenue_jan_apr
X_test = features_may_jun
y_test = revenue_may_jun

# Scale features
scaler = StandardScaler()
X_train_scaled = scaler.fit_transform(X_train)
X_test_scaled = scaler.transform(X_test)

# Fit model
model1 = LinearRegression()
model1.fit(X_train_scaled, y_train)

# Evaluate
y_pred = model1.predict(X_test_scaled)
rmse = np.sqrt(mean_squared_error(y_test, y_pred))
r2 = r2_score(y_test, y_pred)
```

**Evaluation Metrics:**
- [ ] R² score (variance explained)
- [ ] RMSE (prediction error in $/min)
- [ ] MAE (mean absolute error)
- [ ] Feature importance (coefficient values)

**Analysis:**
- [ ] Which features most strongly predict revenue?
- [ ] Do external factors (weather, events) significantly improve predictions?
- [ ] Residual analysis: Where does the model fail? (specific zones?)

**Deliverables:**
- [ ] Model performance table (R², RMSE, MAE)
- [ ] Feature importance plot (coefficients)
- [ ] Residual plot (predicted vs. actual, or residuals vs. fitted)

### 6.2 Model 2: Random Forest or Gradient Boosting
**Classification: "High Revenue" vs. "Low Revenue" Zone-Months**

**Setup:**
- [ ] Define target: Binary classification
  - High revenue: revenue_per_minute > city median
  - Low revenue: revenue_per_minute <= city median
- [ ] Use same features as Model 1
- [ ] Split: Jan-Apr (train), May-Jun (test)

**Implementation:**
```python
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import classification_report, confusion_matrix, roc_auc_score

model2 = RandomForestClassifier(n_estimators=100, max_depth=10, random_state=42)
model2.fit(X_train, y_train)

y_pred = model2.predict(X_test)
y_pred_proba = model2.predict_proba(X_test)[:, 1]

# Metrics
print(classification_report(y_test, y_pred))
print(confusion_matrix(y_test, y_pred))
roc_auc = roc_auc_score(y_test, y_pred_proba)
```

**Evaluation Metrics:**
- [ ] Accuracy, Precision, Recall, F1-score
- [ ] Confusion matrix
- [ ] ROC-AUC score
- [ ] Feature importance (tree-based)

**Analysis:**
- [ ] Which features best distinguish high vs. low revenue periods?
- [ ] Can the model identify underperforming zones in advance?
- [ ] Do external factors help predict high/low revenue?

**Deliverables:**
- [ ] Model performance table (Accuracy, Precision, Recall, F1, AUC)
- [ ] Feature importance plot (top 10 features)
- [ ] Confusion matrix visualization

### 6.3 Model Comparison & Interpretation
**Notebook: `05_modeling.ipynb` & Code: `src/modeling.py`**

- [ ] Compare Model 1 and Model 2:
  - Which performs better? (On what metric?)
  - What are trade-offs? (Interpretability vs. accuracy?)
  - Do they agree or disagree on important features?

**Analysis for report:**
> "Model 1 (Linear Regression) explains 65% of variance in revenue (R²=0.65), with external factors accounting for ~15% of this explanatory power. Model 2 (Random Forest) achieves higher accuracy (78%) at classification but is less interpretable. Both models identify weather and month as key predictors, suggesting that vendors cannot fully control revenue outcomes and should adapt staffing seasonally."

---

## PHASE 7: PRELIMINARY FINDINGS & INTERPRETATION (Week 4)

### 7.1 Synthesis: Analysis Meets Modeling
**Notebook: `04_analysis.ipynb` + `05_modeling.ipynb`**

**Key Findings Template:**

1. **Which zones underperform?**
   - List 5 worst zones (by combined metric: neighbor-based + temporal)
   - Quantify: "Zone X earns 25% less than neighbors and declined 30% over 6 months"

2. **What external factors explain it?**
   - Weather: "Precipitation reduces revenue by ~12% on average; Zone Q has X% more rainy days"
   - Events: "Major events nearby increase demand, but Zone Q has fewer events"
   - Time patterns: "Zone Q underperforms during peak hours (mornings/weekends)"

3. **Model insights:**
   - "Our regression model shows weather explains 8% of revenue variance; events explain 5%"
   - "However, zone identity explains 40% of variance, suggesting inherent zone characteristics matter most"

### 7.2 Interpretation & Discussion
- [ ] Why do these zones underperform?
  - Controllable factors (staffing, pricing, promotions)?
  - Uncontrollable factors (geographic location, demand patterns)?
  - Changing factors (construction, economic shifts)?
- [ ] Are findings surprising?
  - If yes: why? What does this tell us?
  - If no: what do expected patterns reveal?

**Questions to probe deeper:**
- Is underperformance a problem to solve or a reality to accept?
- Can external factors be leveraged by vendors?
- Are some zones fundamentally limited?

---

## PHASE 8: RECOMMENDATIONS (Week 4)

### 8.1 Develop Vendor Strategies
**Based on findings, create 3-4 specific recommendations:**

**Format for each recommendation:**
1. **Statement:** Clear, actionable recommendation
2. **Justification:** Evidence from analysis & modeling
3. **Implementation:** How vendors actually do this
4. **Expected Impact:** Quantified outcome (if possible)

**Example:**
> **Recommendation 1: Seasonal Driver Reallocation**
> 
> *Statement:* Vendors should increase driver presence in high-performing zones during winter months (Jan-Mar) when overall demand is lower and concentrated in specific zones.
> 
> *Justification:* Our analysis shows Zone X's revenue peaks in winter while neighboring Zone Y remains stable year-round. Weather analysis reveals Zone X's spike correlates with reduced supply (fewer drivers available) and concentrated demand near transit hubs. Our model predicts that 10% increase in driver supply in Zone Y during winter would improve zone profitability by ~15%.
> 
> *Implementation:* Track monthly revenue trends by zone. When a zone shows downward trajectory (like Zone Q Jan-Jun), redeploy 2-3 drivers from stable high-volume zones for 4-6 week trial periods.
> 
> *Expected Impact:* Estimated revenue recovery of $50-100 per driver per week in underperforming zones; improved overall fleet utilization.

**Recommendation 2-4:**
- [ ] Develop 2-3 more recommendations
- [ ] Ensure each is specific, not generic
- [ ] Root in your analysis/models
- [ ] Realistic to implement

### 8.2 Address Limitations & Caveats
- [ ] What can't your analysis explain?
- [ ] What confounding factors exist?
- [ ] What would you need to prove causation?

---

## PHASE 9: REPORT WRITING (Week 4-5)

### 9.1 LaTeX Setup
- [ ] Download LaTeX template from Canvas/Overleaf
- [ ] Create Overleaf project (or local setup)
- [ ] Set document class and margins per spec:
  ```latex
  \documentclass[11pt]{article}
  \usepackage[top=0.9in, left=0.9in, bottom=0.9in, right=0.9in]{geometry}
  ```

### 9.2 Report Structure (6-8 pages)

**Page Budget (approximate):**
- Intro: 1 page
- Methodology: 0.5 pages
- EDA/Analysis: 1.5 pages (with figures)
- Modeling: 1.5 pages (with tables)
- Recommendations: 1 page
- Conclusion: 0.5 pages
- References: separate

**Detailed Outline:**

**1. Introduction (1 page, 4 marks)**
- [ ] Opening sentence: Hook the reader (why should vendors care?)
- [ ] Problem statement: Which zones underperform? Why matters?
- [ ] Dataset: Timeline (Jan-Jun 2019), type (Yellow taxis), shape (rows/columns)
- [ ] Target audience: Fleet managers/vendors
- [ ] Research goal: Identify underperformers + external factors + recommendations
- [ ] Assumptions: Neighbors have similar demand; external factors affect performance
- [ ] High-level methodology (TLDR of contribution)
- [ ] Justification: Why this timeline? Why these zones? Why these external factors?

**2. Preprocessing (0.5 page, 2 marks)**
- [ ] Bullet points (concise):
  - Data source, format, shape
  - Cleaning decisions (outliers removed, missing values handled)
  - External data: Weather (source), events (source)
  - Final dataset shape (before/after each major step)
- [ ] Justification for any removals (cite TLC business rules)

**3. Analysis & Visualization (1.5 pages, 4 marks)**
- [ ] Outlier analysis: Distribution of revenue per minute, null values handled
- [ ] Underperformance metric: How defined? (neighbor comparison)
- [ ] Geospatial visualization: Map of underperforming zones
- [ ] Temporal analysis: Revenue trends over 6 months
- [ ] External factors: How do they correlate with revenue?
- [ ] Key figures:
  - Figure 1: Geospatial map (underperforming zones)
  - Figure 2: Time-series of top underperformers
  - Figure 3: Revenue patterns (time-of-day, day-of-week)
  - Figure 4 (optional): External factors overlay

**4. Statistical Modelling (1.5 pages, 4 marks)**
- [ ] Model 1: Linear Regression
  - Justification (why this model?)
  - Features & assumptions
  - Results (R², RMSE, feature importance)
  - Interpretation: What does this tell us?
- [ ] Model 2: Random Forest/Classification
  - Justification (why this model?)
  - Results (accuracy, AUC, confusion matrix)
  - Interpretation: What does this tell us?
- [ ] Model Comparison: Which is better? Why?
- [ ] Key tables:
  - Table 1: Model performance comparison
  - Table 2: Feature importance (top 10 features)

**5. Recommendations (1 page, 6 marks)**
- [ ] Recommendation 1 (3 marks)
  - Clear, specific statement
  - Evidence from analysis/models
  - Practical implementation
- [ ] Recommendation 2 (3 marks)
  - As above
- [ ] (Optional) Recommendation 3-4
- [ ] Each recommendation must:
  - ✅ Be non-generic (not "hire more drivers")
  - ✅ Be rooted in your analysis
  - ✅ Be practical (vendors can actually do it)
  - ✅ Show expected impact

**6. Conclusion & Limitations (0.5 page)**
- [ ] Summary of findings
- [ ] Limitations (causation vs. correlation, external factors we couldn't measure)
- [ ] Future work (what else would you investigate?)

### 9.3 Figures & Tables
- [ ] All figures referenced in text: "As shown in Figure X..."
- [ ] Readable font size (12pt min for axis labels)
- [ ] Appropriate color schemes (colorblind-friendly)
- [ ] Clear captions: "Figure X: Description of what to look for"
- [ ] All tables: Clear headers, units specified
- [ ] No code in report (only outputs)

### 9.4 Writing Quality
- [ ] Proofread multiple times
- [ ] Check for consistency (zones labeled consistently, metrics defined clearly)
- [ ] Use tools: Grammarly, spell-check (but not AI to generate text)
- [ ] Peer review: Have someone else read it
- [ ] Professional tone: Write as if a client is paying you

### 9.5 Citations & References
- [ ] Cite data sources: TLC dataset, NOAA weather, event sources
- [ ] Cite methods: Linear regression, Random Forest (reference to theory if novel)
- [ ] Use consistent citation style (APA recommended)
- [ ] Reference section on separate page

---

## PHASE 10: CODE QUALITY & GITHUB (Week 4-5)

### 10.1 Code Organization
- [ ] Each notebook has clear structure:
  - Headers: `# Section name`
  - Markdown cells explaining each step
  - Docstrings for functions
- [ ] Separate functions in `src/` modules:
  - `src/preprocessing.py`: Data cleaning functions
  - `src/analysis.py`: Analysis functions (underperformance calc, etc.)
  - `src/modeling.py`: Model training/evaluation
- [ ] All functions have docstrings:
  ```python
  def calculate_underperformance(zone_revenue, neighbor_revenue):
      """
      Calculate percentage underperformance vs. neighbors.
      
      Args:
          zone_revenue (float): Revenue per minute for zone
          neighbor_revenue (float): Mean revenue of neighbors
      
      Returns:
          float: Underperformance percentage (negative = underperforming)
      """
  ```

### 10.2 Code Comments
- [ ] Inline comments for complex logic
- [ ] Variable names are descriptive (not `x`, `df2`, etc.)
- [ ] No commented-out code (delete it)

### 10.3 README.md
- [ ] Project title & problem statement
- [ ] Data sources & how to obtain them
- [ ] How to run the project:
  ```
  1. Install dependencies: pip install -r requirements.txt
  2. Download data to data/raw/
  3. Run notebooks in order: 01_*.ipynb, 02_*.ipynb, etc.
  4. Or run: python -m src.preprocessing
  ```
- [ ] Project structure (folder overview)
- [ ] Key findings summary
- [ ] Report link

### 10.4 GitHub Commits
- [ ] Regular commits (weekly minimum, ideally 2-3x/week)
- [ ] Descriptive commit messages:
  - ✅ "Add preprocessing script for outlier removal"
  - ❌ "updated notebook"
- [ ] Final commit: "Final submission for MAST30034"

### 10.5 Final Checks
- [ ] Code runs without errors (have someone else try)
- [ ] All notebooks execute top-to-bottom without issues
- [ ] requirements.txt is accurate and complete
- [ ] All data paths are relative (not hardcoded to your computer)
- [ ] Large files (.parquet) not committed; document how to obtain

---

## PHASE 11: FINAL ASSEMBLY & SUBMISSION (Week 5)

### 11.1 Report Assembly
- [ ] Compile LaTeX → PDF
- [ ] Verify formatting: margins, fonts, figure sizes
- [ ] Check page count: 6-8 pages (excluding references)
- [ ] Verify all figures/tables are readable
- [ ] Proofread one final time

### 11.2 GitHub Final Check
- [ ] All notebooks present and working
- [ ] Code clean and well-commented
- [ ] README complete with hyperlink to report
- [ ] requirements.txt accurate
- [ ] One final commit

### 11.3 Submission Checklist
- [ ] Report PDF submitted to Turnitin (LaTeX-compiled, not Word)
- [ ] GitHub link hyperlinked in report (or submitted separately per spec)
- [ ] Filename format: `[StudentID]_MAST30034_Report.pdf`
- [ ] Test submission: Can you download it and view it?

### 11.4 Buffer Time
- [ ] Aim to have everything done by August 24-25
- [ ] Reserve 6 days for proofreading, fixes, re-renders
- [ ] Deadline: August 31, 11:59 PM

---

## TIMELINE SUMMARY

| Week | Phase | Deliverables |
|------|-------|--------------|
| Week 1 | Data sourcing + EDA | Clean dataset, underperformance metrics defined |
| Week 2 | External data + Analysis | Weather/events integrated, 5-10 target zones identified |
| Week 3 | Modeling | Two models built, evaluated, compared |
| Week 4 | Synthesis + Recommendations | Key findings, 3-4 recommendations, first report draft |
| Week 4-5 | Report writing | Final report (6-8 pages, LaTeX, PDF) |
| Week 5 | Code cleanup + Submission | GitHub polished, report submitted |

---

## Key Reminders

✅ **Do these:**
- Start immediately (don't delay)
- Commit to GitHub regularly
- Document all decisions (esp. data cleaning)
- Test code frequently
- Proofread report multiple times
- Make sure recommendations are specific & non-generic

❌ **Avoid these:**
- Leaving report writing to last week
- Hardcoding paths or data splits
- Generic recommendations ("hire more drivers")
- Figures too small to read
- Forgetting to cite external data sources
- Submitting code that doesn't run

---

## Success Criteria

By the end, you should be able to answer:

1. **Which zones underperform?** (5-10 specific zones, quantified)
2. **Why do they underperform?** (external factors identified + modeled)
3. **What should vendors do?** (3-4 specific, practical recommendations)
4. **How confident are you?** (supported by statistical models & analysis)

Good luck! You've got this. 🚕📊
