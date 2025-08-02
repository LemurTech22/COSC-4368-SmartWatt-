# COSC-4368-SmartWatt
Team Members: Jose Conde, Clark Horak, Adam Nguyen, Ben Tuason

Our code was written in Google Colab.

How to run: 
Ensure you have a virtual Environment created on your system.
activate your Virtual Environment 


install these packages to run: Tensorflow, numpy, pandas, matplotlib, and meteostat

pip install Tensorflow
pip install numpy
pip install pandas
pip install matplotlib
pip install meteostat
pip install keras
pip install keras-models

Have a virtual environment set up to plot 

further questions please feel free to reach out to any collaborators.

Project Description

This project was completed in collaboration with a startup called SmartWatts, which provided us with two years of residential energy usage data — approximately 900,000 records collected at 15-minute intervals. Our task was to explore the dataset, generate insights, and propose ways to model and forecast energy consumption patterns.

We hypothesized that temperature would be a key driver of energy usage, especially during extreme heat in Texas, when cooling demand spikes. To test this, we integrated weather data from the Meteostat API, aligning historical temperature data with energy usage timestamps. Since the API only included data up to the current date, we needed to forecast both temperature and energy usage into the future.

The data was preprocessed by removing irrelevant features, handling missing values, and scaling to account for outliers. Each user’s energy profile was isolated to train models individually, with generalization tested across users. We found a strong correlation between temperature and energy use, validating our hypothesis.

For modeling, we trained and evaluated three deep learning architectures: Recurrent Neural Networks (RNNs), Long Short-Term Memory (LSTM), and Gated Recurrent Units (GRU). After comparing model performance, LSTM outperformed the others with a 97% accuracy rate. We validated this by holding out a full month of data and comparing forecasted values to actual readings, achieving approximately 95% match. Confidence intervals were used to assess the reliability of the forecasts.
