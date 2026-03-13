# ⚖️ Python BMI Calculator & Tracker

A sleek, desktop-based Body Mass Index (BMI) calculator and health tracking application built with Python, Tkinter, and Matplotlib. 

This app doesn't just calculate your BMI once; it allows you to create user profiles, set health goals, and visualize your weight and BMI trends over time with interactive graphs.

![Python](https://img.shields.io/badge/Python-3.8+-blue.svg)
![Tkinter](https://img.shields.io/badge/GUI-Tkinter-lightgrey.svg)
![Matplotlib](https://img.shields.io/badge/Data%20Viz-Matplotlib-orange.svg)
![SQLite3](https://img.shields.io/badge/Database-SQLite3-green.svg)

---

## ✨ Features

* **👥 Multi-User Profiles:** Create and switch between different profiles to track health metrics for multiple people.
* **🎯 Goal Setting:** Set target weights and target BMIs to stay motivated. The app calculates how far off you are from your goal with every new entry.
* **📊 Visual Trend Analysis:** Embedded Matplotlib graphs display your historical BMI and weight data over time, overlaying your target lines for easy tracking.
* **🌓 Dark/Light Mode:** Seamlessly toggle between light and dark themes with a single click. The graphs automatically adjust their colors to match the theme.
* **📅 Built-in Date Picker:** Easily log historical data with a simple, integrated date picker.
* **💾 Local Database:** All records and profiles are securely saved locally using a lightweight SQLite database (`bmi_history.db`).

---

## 🛠️ Installation & Setup

### Prerequisites
Make sure you have Python installed on your system (Python 3.8 or higher is recommended).

### 1. Clone the Repository
```bash
git clone [https://github.com/Chethana812/bmi-calculator.git](https://github.com/yourusername/bmi-calculator.git)
cd bmi-calculator