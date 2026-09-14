# Strava Gear & Shoes Tracker for Home Assistant 👟🚲

[![HACS Custom Repository](https://img.shields.io/badge/HACS-Custom-orange.svg)](https://hacs.xyz/)
[![Home Assistant](https://img.shields.io/badge/Home--Assistant-2024.1+-blue.svg)](https://www.home-assistant.io/)

A dedicated Home Assistant integration for tracking all your **running shoes and bikes** from Strava. Features wear percentages, remaining mileage calculations, and critical replacement binary sensors.

---

## ✨ Features
- 👟 **Individual Shoe Sensors**: Tracks current distance, remaining distance to max lifespan (e.g. 800 km), and wear %.
- 🚲 **Individual Bike Sensors**: Tracks gravel, road, and mountain bike mileage.
- ⚠️ **Wear Alert Binary Sensors**: Turns `ON` when a shoe reaches 95% or 100% wear to trigger automated replacement notifications.
- ⚡ **Auto-refresh & OAuth**: Automatically refreshes Strava OAuth tokens.

---

## 🚀 Installation via HACS
1. In Home Assistant, open **HACS** > **Integrations** > **Custom repositories**.
2. Add this repo URL with category **Integration**.
3. Download and restart Home Assistant.
4. Go to **Settings** > **Devices & Services** > **Add Integration** > **Strava Gear**.
