<p align="center">
  <img src="icon.png" width="160" height="160" alt="Strava Gear Home Assistant Icon" />
</p>

# Strava Gear & Shoes Tracker for Home Assistant 👟🚲

[![HACS Custom Repository](https://img.shields.io/badge/HACS-Custom-orange.svg)](https://hacs.xyz/)
[![Home Assistant](https://img.shields.io/badge/Home--Assistant-2024.1+-blue.svg)](https://www.home-assistant.io/)
[![License: GPL v3](https://img.shields.io/badge/License-GPLv3-blue.svg)](https://www.gnu.org/licenses/gpl-3.0)
[![Buy Me A Coffee](https://img.shields.io/badge/Buy%20Me%20A%20Coffee-Support-yellow.svg?style=flat&logo=buy-me-a-coffee)](https://buymeacoffee.com/lediabloteur)

A dedicated Home Assistant integration for tracking all your **running shoes and bikes** from Strava. Features wear percentages, remaining mileage calculations, and critical replacement binary sensors.

---

## ✨ Features
- 👟 **Individual Shoe Sensors**: Tracks current distance, distance limit defined on Strava (`notification_distance` / `max_km`), remaining distance, and wear %.
- 🚲 **Individual Bike Sensors**: Tracks gravel, road, and mountain bike mileage with wear metrics if a distance limit is defined.
- 🎯 **Automatic Strava Limit Sync**: Directly synchronizes the distance notification limit set on Strava for each piece of equipment.
- ⚠️ **Wear Alert Binary Sensors**: Turns `ON` when gear reaches 95% or 100% wear to trigger automated replacement notifications.
- ⚡ **Auto-refresh & OAuth**: Automatically refreshes Strava OAuth tokens and discovers gear from profile and recent activities.

---

## 🚀 Installation via HACS
1. In Home Assistant, open **HACS** > **Integrations** > **Custom repositories**.
2. Add this repo URL with category **Integration**.
3. Download and restart Home Assistant.
4. Go to **Settings** > **Devices & Services** > **Add Integration** > **Strava Gear**.

---

## ☕ Support the Project

If this integration helps you keep track of your running shoes or bike components, consider supporting the project!

<p align="left">
  <a href="https://buymeacoffee.com/lediabloteur" target="_blank">
    <img src="https://cdn.buymeacoffee.com/buttons/v2/default-yellow.png" alt="Buy Me A Coffee" width="180" />
  </a>
</p>

## 📄 License

This project is licensed under the **GNU General Public License v3.0 (GPLv3)** - see the [LICENSE](LICENSE) file for details.
