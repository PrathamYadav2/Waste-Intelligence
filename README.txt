================================================================================
  AI-BASED WASTE SEGREGATION, RECYCLING ANALYTICS & REGIONAL DECISION SYSTEM
================================================================================

PROJECT OVERVIEW:
-----------------
An End-to-End Decision Intelligence Platform combining Deep-Learning Computer
Vision (MobileNetV3), Explainable AI (Grad-CAM), Deep Recycling Potential Analytics,
and Regional Time-Series Forecasting across 12 Maharashtra municipal corporations.


HOW TO RUN THE PROJECT (SABSE AASAN TARIKA):
--------------------------------------------
1. Iss folder me 'start.bat' par double click karein.
   (Ya 'Launch_Waste_AI.bat' par double click karein).
2. Server automatically start ho jayega aur browser me yeh link open hogi:
   http://127.0.0.1:8000/
3. Browser me aap:
   - Koi bhi photo upload karke AI waste detection dekh sakte hain.
   - Grad-CAM heatmap dekh sakte hain.
   - Recycling potential aur scrap market rate (Rs./kg) check kar sakte hain.
   - 2024-2027 regional forecasting map aur table inspect kar sakte hain.


AI VISION CLASSIFIER SPECIFICATIONS:
-------------------------------------
- Architecture:       PyTorch MobileNetV3-Small
- Weights File:       models/image_classifier/realwaste_mobilenet_v3.pth (6.24 MB)
- Accuracy on Test:   78.26%
- Macro F1-Score:     79.26%
- Training Dataset:   RealWaste (4,752 real-world images)
- 9 Classes Detected:
  1. Cardboard             -> Blue Bin (Dry Recyclable)
  2. Food Organics         -> Green Bin (Wet Waste)
  3. Glass                 -> Blue Bin (Cullet Recycling)
  4. Metal                 -> Blue Bin (High Value Alloy)
  5. Miscellaneous Trash   -> Black Bin (Inerts / RDF)
  6. Paper                 -> Blue Bin (Fibre Pulp)
  7. Plastic               -> Blue Bin (PET / Polymers)
  8. Textile Trash         -> Special Recovery / Felt
  9. Vegetation            -> Green Bin (Compost / Bio-CNG)


REGIONAL FORECASTING RESULTS (2024 - 2027):
-------------------------------------------
- Model: Damped Linear Trend Forecaster (MAE: 72.07 TPD, MAPE: 3.17%)
- Evaluated on 12 Maharashtra Urban Local Bodies:
  * Pune:        4,439.9 TPD (2023)  ->  4,723.2 TPD (2027)  [+283.2 TPD (+6.4%)]
  * Nashik:      2,245.1 TPD (2023)  ->  2,375.7 TPD (2027)  [+130.6 TPD (+5.8%)]
  * Thane:       2,148.9 TPD (2023)  ->  2,266.5 TPD (2027)  [+117.6 TPD (+5.5%)]
  * Nagpur:      1,688.0 TPD (2023)  ->  1,778.3 TPD (2027)  [+90.3 TPD (+5.3%)]
  * Aurangabad:  1,858.6 TPD (2023)  ->  1,939.8 TPD (2027)  [+81.3 TPD (+4.4%)]
  * Chandrapur:    503.5 TPD (2023)  ->    549.3 TPD (2027)  [+45.8 TPD (+9.1%)]
  * Amravati:      809.9 TPD (2023)  ->    843.2 TPD (2027)  [+33.2 TPD (+4.1%)]
  * Kolhapur:      823.1 TPD (2023)  ->    845.8 TPD (2027)  [+22.6 TPD (+2.7%)]
  * Raigad:        593.4 TPD (2023)  ->    743.2 TPD (2027)  [+149.8 TPD (+25.2%)]
  * Navi Mumbai:   743.0 TPD (2023)  ->    735.9 TPD (2027)  [-7.1 TPD (-1.0%)]
  * Kalyan:      1,606.0 TPD (2023)  ->  1,540.5 TPD (2027)  [-65.5 TPD (-4.1%)]
  * Mumbai:      6,690.0 TPD (2023)  ->  5,967.0 TPD (2027)  [-723.0 TPD (-10.8%)]


RECYCLING POTENTIAL & SCRAP MARKET BENCHMARK:
---------------------------------------------
Har detected material ke liye real economic benchmarks:
- Aluminium Scrap:      Rs. 125 - 155 / kg (Infinite recycling loops)
- PET Plastic Bottles:  Rs. 26 - 38 / kg   (2-3 mechanical cycles)
- Corrugated Cardboard: Rs. 11 - 15 / kg   (5-7 fiber cycles)
- Glass Cullet:         Rs. 2.5 - 4.5 / kg (Infinite recycling loops)


IMPORTANT NOTE ON '.pth' MODEL FILES:
-------------------------------------
Agar aapne 'models/image_classifier/realwaste_mobilenet_v3.pth' par click kiya
hai aur woh nahi khul raha:
- .pth file PyTorch binary weights hoti hai, koi executable program (.exe) nahi.
- Isko chalane ke liye 'start.bat' double click karein ya 'python predict.py' run karein.


FOLDER STRUCTURE:
-----------------
Waste Project/
├── README.txt              <-- Yeh text file (Notepad me direct khulegi)
├── README.html             <-- Web format file (Browser me direct khulegi)
├── README.md               <-- Full Markdown documentation
├── start.bat               <-- 1-Click Windows Launcher (Auto-opens browser)
├── run.bat                 <-- Alternate Windows Launcher
├── run.sh                  <-- Linux / Git Bash Runner
├── app.py                  <-- FastAPI Server
├── predict.py              <-- Quick CLI image test script
├── app/                    <-- Frontend Dashboard (index.html)
├── models/                 <-- Trained PyTorch model weights (.pth)
├── data/processed/         <-- 2024-2027 Forecast CSV files
├── Project Data/           <-- Image Data & Maharashtra Regional Data
└── src/                    <-- Vision, Forecasting & Recommendation Engine code
================================================================================
