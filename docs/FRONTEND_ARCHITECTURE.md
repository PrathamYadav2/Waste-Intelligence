# Frontend Architecture
Static, accessible, responsive pages in `app/`, served by FastAPI. CSS: `tokens.css` -> `base.css` -> `layout.css` -> `components.css`. Page states are driven by `data-state` (empty/loading/error/ready); `?state=` is a review helper only. Charts/maps libraries: TO_BE_VERIFIED_DURING_IMPLEMENTATION. Signature element: the **recovery chain** (Image -> Waste type -> Material -> Recovery score -> Route).

## Pages

### 1. Dashboard (`app/index.html`)
- **Purpose:** Single-glance view of recovery activity and regional waste pressure.
- **Components:** Recent scans, Waste pressure by region, Priority regions, Open community actions
- **Data requirements:** Recent observations, regional summary, priority list, action counts
- **API requirements:** GET /regional/overview, GET /recommendations, GET /models
- **UX flow:** Land -> scan recent activity -> open a region or start a scan
- **Loading state:** skeleton blocks, `aria-busy=true`.
- **Error state:** inline alert with cause and Retry; links to System & Data Health.
- **Empty state:** "No scans yet. Scan a waste item to start building your recovery record."

### 2. AI Waste Scanner (`app/scanner.html`)
- **Purpose:** Capture or upload a waste image and optional context for analysis.
- **Components:** Image upload, Context (region, condition)
- **Data requirements:** Image file, optional region, optional manual condition
- **API requirements:** POST /waste/analyze
- **UX flow:** Choose image -> validate type/size -> optional context -> Analyze -> Result page
- **Loading state:** skeleton blocks, `aria-busy=true`.
- **Error state:** inline alert with cause and Retry; links to System & Data Health.
- **Empty state:** "Add a photo of a single waste item to begin."

### 3. Waste Analysis Result (`app/result.html`)
- **Purpose:** Show what the model saw: waste type, material, confidence and the recovery path.
- **Components:** Prediction, Confidence, Recovery score, Top alternatives
- **Data requirements:** ClassifyResponse, RecoveryResponse, model version
- **API requirements:** POST /waste/analyze (response), GET /models
- **UX flow:** Result loads -> read chain -> open Recovery or Explainable AI -> save as observation
- **Loading state:** skeleton blocks, `aria-busy=true`.
- **Error state:** inline alert with cause and Retry; links to System & Data Health.
- **Empty state:** "No analysis to show. Start from the AI Waste Scanner."

### 4. Recovery Recommendation (`app/recovery.html`)
- **Purpose:** Explain the recommended recovery route and why.
- **Components:** Recommended route, Score factor breakdown, Rule / ML / scoring trace, Community action
- **Data requirements:** Route, score + factor_breakdown, component_trace, community action
- **API requirements:** POST /recovery/recommend
- **UX flow:** Review route -> inspect factors -> accept community action
- **Loading state:** skeleton blocks, `aria-busy=true`.
- **Error state:** inline alert with cause and Retry; links to System & Data Health.
- **Empty state:** "No recommendation yet. Analyze an item first."

### 5. Regional Waste Intelligence (`app/regional.html`)
- **Purpose:** Compare regional waste generation and pressure.
- **Components:** Regional comparison, Generation trend, Region table, Pressure indicators
- **Data requirements:** Regional waste records (target gen_total_ulb_tpd), pressure index
- **API requirements:** GET /regional/overview, GET /regional/{region}
- **UX flow:** Pick region(s) -> compare trends -> open forecast
- **Loading state:** skeleton blocks, `aria-busy=true`.
- **Error state:** inline alert with cause and Retry; links to System & Data Health.
- **Empty state:** "Regional data is not connected. Set REGIONAL_DATA_PATH and run data validation."

### 6. Forecast & Capacity Planning (`app/forecast.html`)
- **Purpose:** Forecast waste generation and show capacity gaps.
- **Components:** Forecast chart, Model used, Capacity gap, Priority regions
- **Data requirements:** Forecast per region/year, model version, capacity (source unverified), gap
- **API requirements:** GET /forecast
- **UX flow:** Select region + horizon -> review forecast and uncertainty -> view gap -> open recommendations
- **Loading state:** skeleton blocks, `aria-busy=true`.
- **Error state:** inline alert with cause and Retry; links to System & Data Health.
- **Empty state:** "No forecast available. Train a forecasting model first."

### 7. Interactive Waste Map (`app/map.html`)
- **Purpose:** Locate regions and visualise pressure geographically.
- **Components:** Map, Layer control, Region details
- **Data requirements:** Region latitude/longitude, selected metric layer
- **API requirements:** GET /map
- **UX flow:** Choose layer -> select region marker -> open regional page
- **Loading state:** skeleton blocks, `aria-busy=true`.
- **Error state:** inline alert with cause and Retry; links to System & Data Health.
- **Empty state:** "Map data is not connected. Latitude/longitude come from the regional dataset."

### 8. Community Action (`app/community.html`)
- **Purpose:** Turn analysis into actions people can take and track.
- **Components:** Suggested actions, Action status, Region campaigns
- **Data requirements:** Recommendations, community_actions with status
- **API requirements:** GET /recommendations
- **UX flow:** Review suggestion -> accept -> mark complete
- **Loading state:** skeleton blocks, `aria-busy=true`.
- **Error state:** inline alert with cause and Retry; links to System & Data Health.
- **Empty state:** "No actions yet. Actions appear after an analysis or forecast run."

### 9. Model Performance (`app/model-performance.html`)
- **Purpose:** Report real evaluation results of classifier and forecaster.
- **Components:** Cross-dataset accuracy, Per-class precision / recall / F1, Confusion matrix, Forecast error metrics
- **Data requirements:** Stored evaluation runs: RealWaste, TrashNet, TACO, forecasting metrics
- **API requirements:** GET /models
- **UX flow:** Pick model version -> pick dataset -> inspect metrics
- **Loading state:** skeleton blocks, `aria-busy=true`.
- **Error state:** inline alert with cause and Retry; links to System & Data Health.
- **Empty state:** "No evaluation runs recorded. Run the evaluation pipeline."

### 10. Explainable AI (`app/explainable-ai.html`)
- **Purpose:** Show which image regions influenced a prediction (Grad-CAM).
- **Components:** Original image, Grad-CAM overlay, Explanation text
- **Data requirements:** Image, real Grad-CAM heatmap, predicted class
- **API requirements:** POST /waste/analyze (explain option) - NOT_IMPLEMENTED_YET
- **UX flow:** Open from a result -> toggle overlay -> read explanation
- **Loading state:** skeleton blocks, `aria-busy=true`.
- **Error state:** inline alert with cause and Retry; links to System & Data Health.
- **Empty state:** "No explanation available. Heatmaps are generated only from a trained model."

### 11. System & Data Health (`app/system-health.html`)
- **Purpose:** Show whether data, models, database and API are ready.
- **Components:** Service status, Dataset connection checks, Validation reports, Active model versions
- **Data requirements:** Health components, validation reports, model registry
- **API requirements:** GET /health, GET /models
- **UX flow:** Check statuses -> open failing check -> follow fix hint
- **Loading state:** skeleton blocks, `aria-busy=true`.
- **Error state:** inline alert with cause and Retry; links to System & Data Health.
- **Empty state:** "Health checks have not run."

