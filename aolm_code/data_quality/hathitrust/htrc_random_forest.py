# Pandas is used for data manipulation
import pandas as pd

# Read in data as pandas dataframe and display first 5 rows
data_csv = "/Users/PeregrinePickle/Documents/School/New York University/Dissertation/Scripts/htrc/output/bibapi_pubdates_titlelens.csv"
features = pd.read_csv(data_csv)

# Use numpy to convert to arrays
import numpy as np

# Labels are the values we want to predict
desired_predict_feature = "title_length"
labels = np.array(features[desired_predict_feature])
# print features.columns

# Remove the labels from the features
# axis 1 refers to the columns
features= features.drop(desired_predict_feature, axis = 1)

# Saving feature names for later use
feature_list = list(features.columns)

# Convert to numpy array
features = np.array(features)

# Using Skicit-learn to split data into training and testing sets
from sklearn.model_selection import train_test_split

# Split the data into training and testing sets
train_features, test_features, train_labels, test_labels = train_test_split(features, labels, test_size = 0.25,
                                                                           random_state = 42)

# The baseline predictions are the historical averages
baseline_preds = test_features[:, feature_list.index("average_title_length")]

# Baseline errors, and display average baseline error
baseline_errors = abs(baseline_preds - test_labels)
print("Average baseline error: ", round(np.mean(baseline_errors), 2), "words.") 

# Import the model we are using
from sklearn.ensemble import RandomForestRegressor

# Instantiate model 
rf = RandomForestRegressor(n_estimators= 1000, random_state=42)

# Train the model on training data
rf.fit(train_features, train_labels);

# Use the forest's predict method on the test data
predictions = rf.predict(test_features)

# Calculate the absolute errors
errors = abs(predictions - test_labels)

# Print out the mean absolute error (mae)
print("Mean Absolute Error:", round(np.mean(errors), 2), "words.")

# Calculate mean absolute percentage error (MAPE)
mape = 100 * (errors / test_labels)
print(errors)
print(test_labels)
print(mape)

# Calculate and display accuracy
accuracy = 100 - np.mean(mape)
print("Accuracy:", round(accuracy, 2), "%.")


