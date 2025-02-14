# Loading libraries
import pandas as pd
import sklearn
import numpy as np
import math
import os
from statistics import mean
from sklearn.metrics import mean_absolute_error, mean_squared_error, f1_score, average_precision_score, accuracy_score, precision_recall_curve, roc_curve, roc_auc_score, confusion_matrix
from sklearn.model_selection import train_test_split, cross_val_score
from sklearn.ensemble import RandomForestClassifier
import matplotlib.pyplot as plt
import pickle


print(os.getcwd())


# Loading data, might want to replace this with a json loader
dataRaw = pd.read_csv('https://raw.githubusercontent.com/jwaldroop/phishing-url-project/main/dataset_full.csv')

# Noticed a discrepancy in the data, some values are recorded as -1 even though it makes not practical sense, i.e. you can't have a negative quantity of a character
# This changes all -1 to 0

def remove_negatives(df):
    df[df == -1] = 0

remove_negatives(dataRaw)

# unit test to check if the negative values are still present

is_it_working = []
def data_cleaning_unit_test(column):
    did_it_work =  {'Yes':0 , 'No':0}
    for i in column:
        if i >= 0:
            did_it_work['Yes'] += 1 # This tracks the number of values that are non-negative
        elif i <0:
            did_it_work['No'] += 1 # This trackes the number of values that are negative
    if did_it_work['No'] > 0:
        print(column.name,'=', 'Not working') # If there are any values that are negative, the script didn't work
    else:
        print(column.name,'=', 'It worked!')

# applying the unit test function to each of the columns in the feature set

for col in dataRaw.columns.tolist(): # this loop applies the unit test function to every column in the data frame
    data_cleaning_unit_test(dataRaw[col]) #

# Setting Target and Features for RF model

Features = dataRaw.iloc[:,:-1] # target is in last column
X = Features
y = dataRaw['phishing']
X.head()

# Split into train and test data

train_X, val_X, train_y, val_y = train_test_split(X, y, random_state=426)

# Loading RF model
# Uses recursive feautre elimination to reduce model inputs

with open('final-RF-model.pkl' , 'rb') as f:
    # pickle the data dictionary using the highest protocol availabe
    model_final = pickle.load(f)

if model_final == model_final:
    print("RF Model Created")
else:
    print("RF Model Failed to Create")

# Saving some validation predicitons and probabilites
val_preds = model_final.predict(val_X)
# predict probabilities
probs = model_final.predict_proba(val_X)
# keep probabilities for the positive outcome only
probs_final = probs[:, 1]

# Evaluating Model
print("Mean Accuracy on Test Data:",model_final.score(val_X,val_y))
print("F1 Score:",f1_score(val_y,val_preds))
print("Average Precision:", average_precision_score(val_y, probs_final)) # second input must be y probability estimates of the positive class

# Going to plot the ROC

# AUC
auc = roc_auc_score(val_y, probs_final)
print('RandomForest: ROC AUC=%.3f' % (auc))

# calculating roc curve
fpr, tpr, thresholds = roc_curve(val_y, probs_final)


# plotting the curve
plt.plot(fpr, tpr, marker='.', label='RandomForest')
# axis labels
plt.xlabel('False Positive Rate')
plt.ylabel('True Positive Rate')
# title
plt.title('ROC curve of {}: AUC={}'.format("Final Model", round(auc, 3)))
# show the legend
plt.legend()
plt.show()


# Precision recall curve
# Calculating values
precision, recall, thresholds = precision_recall_curve(val_y, probs_final)
test_average_precision = average_precision_score(val_y, probs_final)

plt.step(recall, precision, color='b', alpha=0.2, where='post')
plt.fill_between(recall, precision, step='post', alpha=0.2, color='b')
plt.xlabel('Recall')
plt.ylabel('Precision')
plt.ylim([0.0, 1.05])
plt.xlim([0.0, 1.0])
str_average_precision = "{0:.3f}".format(test_average_precision)
plt.title('Precision-Recall curve of {}: AUC={}'.format("Final Model", str_average_precision))
plt.show()

# Confusion Matrix
print('Confusion Matrix: \n', confusion_matrix(val_y,val_preds))


# Cross Validation
print('Beginning Cross Validation')
cv_scores_final = cross_val_score(model_final['m'], X, y, cv=5)
print('Cross Validation Scores: \n' , cv_scores_final)
print('Mean Accuracy From Cross Validation:', mean(cv_scores_final))
