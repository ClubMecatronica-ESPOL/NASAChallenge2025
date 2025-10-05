# <h1 align="left">🦈 Shark Tracker <img src="images/CDMLogo.png" width="100" height="100" align="right"/> </h1>
Predicting Shark Foraging Habitats with NASA Data 🌊

![tracker](images/tracker.jpg)

## 🔍 Project

**Shark Tracker** is an innovative project combining **smart tracking devices**, **NASA satellite data**, and **mathematical models** to predict shark foraging habitats and track their movements in real-time.

This project aims to **better understand sharks**, their foraging patterns, and contribute to **marine ecosystem conservation**.

---

## 🛠 Project Features

* **📡 Shark Tracking Device**

  * Attached to the side of the shark.
  * Generates energy using the shark's natural movement.
  * Sends **real-time location data**.

* **📊 Prediction Algorithm**

  * Uses **shark location data** and **NASA satellite data** (sea surface temperature and phytoplankton).
  * Predicts the **shark's trajectory and foraging habitats**.

* **🌐 Visualization Algorithm**

  * Generates interactive maps and graphs of shark activity.

---

## 🎯 Objectives

1. Identify **shark foraging hotspots**.
2. Quantify the relationship between:

   * Oceanographic features 🌊
   * Phytoplankton communities 🌱
   * Predator movement 🦈
3. Develop a **conceptual smart tag model** to measure diet and location in real-time.

---

## 🧩 How It Works

1. **The device** attaches to the shark and collects position and movement data.
2. **The mathematical algorithm** receives both device and NASA satellite data.
3. **The predictive model** estimates likely shark trajectories and foraging zones.
4. **The visualization module** creates interactive maps and graphs.

---

## 📦 Technologies Used

* **Python** 🐍
* **Pandas / NumPy** for data processing
* **Matplotlib / Seaborn / Plotly** for visualization
* **NASA APIs (PACE & SWOT)** for satellite data
* **Custom IoT device** for shark tracking

---

## 🚀 How to Run the Project

To use this project, you need to:

1. Download sea surface temperature (SST) and chlorophyll concentration data using NASA's OB.DAAC Level 3 & 4 Browser: https://oceandata.sci.gsfc.nasa.gov/l3/
Prepare shark location data in CSV format (id, lat, lon) obtained from the tracker or generated synthetically for testing.

2. Then, clone this repository:

```bash
git clone https://github.com/your-username/shark-tracker.git
```

3. Install dependencies:

```bash
pip install -r requirements.txt
```

4. Run the prediction algorithm:

```bash
python predict_shark_path.py
```

5. Visualize the results:

```bash
python visualize_shark_data.py
```

---

## 🌟 Results

* Global maps of **shark activity**
* Identification of **foraging hotspots**
* Visualization of the relationship between **phytoplankton and sharks**

---

## 📚 References

* NASA PACE Mission: [https://pace.gsfc.nasa.gov/](https://pace.gsfc.nasa.gov/)
* NASA SWOT Mission: [https://swot.jpl.nasa.gov/](https://swot.jpl.nasa.gov/)
* Articles on **shark movement and conservation**

---

## 💡 Next Steps

* Integrate additional sensors to measure **diet in real-time**
* Optimize the predictive model using **machine learning**
* Expand **interactive visualization** into a web dashboard

---

## 🦈 Contact
Sebastian Benitez​ - [123@espol.edu.ec](mailto:@espol.edu.ec)

Abel López Macías​ - [123@espol.edu.ec](mailto:@espol.edu.ec)

Sebastian Mites​ - [123@espol.edu.ec](mailto:@espol.edu.ec)

Sophia Eras Aspiazu​ - [123@espol.edu.ec](mailto:@espol.edu.ec)

William Mayorga - [123wilimayo@espol.edu.ec](mailto:wilimayo@espol.edu.ec)
