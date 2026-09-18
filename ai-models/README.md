# HoneyChain — AI Models Layer (`/ai-models`)

## Overview

The AI layer for **HoneyChain** (SIH 2026 Problem Statement 26021, Ministry of MSME / KVIC).

Apiculture faces two major challenges:
1. **Pest & Disease Losses**: Varroa destructor mites and American/European Foulbrood can decimate 40–60% of colonies if undetected.
2. **Unpredictable Harvests**: Fluctuating weather and bloom periods make it difficult for rural beekeepers and cooperatives to plan extraction, packaging, and forward contracts.

---

## Models Included

### 1. MobileNet Hive Frame Disease Classifier (`disease_detector.py`)
- Lightweight image classification architecture designed for low-latency inference on mobile/edge devices.
- Classes:
  - `Healthy Brood Comb`
  - `Varroa Mite Infestation`
  - `American Foulbrood`
- Returns diagnostic confidence, urgency window (hours), and plain-language treatment advice.
- Edge quantization profile provided in [`export_tflite.py`](export_tflite.py) yielding a compact **2.4 MB** model runnable directly on budget Android devices.

### 2. Honey Harvest Productivity Predictor (`yield_predictor.py`)
- Multi-variate regression forecasting 14-day net extractable honey yield (in kg) and anticipated revenue.
- Features:
  - Daily net colony weight trend (kg/day from load cell)
  - Temperature & humidity suitability index
  - Regional floral bloom phenology factor

---

## Running Inference

```bash
# Run disease classifier
python disease_detector.py --image sample_images/varroa_test.jpg

# Run yield regression forecast
python yield_predictor.py --trend 0.85 --temp 34.8 --days 14
```
