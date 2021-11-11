# Import required packages:

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import sklearn
from sklearn.linear_model import LinearRegression
from sklearn.model_selection import train_test_split
from sklearn.metrics import r2_score
from sklearn.metrics import mean_squared_error
import seaborn as sns
import statsmodels.api as sm
import statsmodels.formula.api as smf
import scipy.stats as stats
from statsmodels.stats.diagnostic import het_white

# West, Welch, and Gatecki (2015, p.9) provide a good definition of fixed-effects and random-effects "Fixed-effect
# parameters describe the relationships of the covariates to the dependent variable for an entire population,
# random effects are specific to clusters of subjects within a population."

# Fixed factors are the independent variables that are of interest to the study, e.g. treatment category,
# sex or gender, categorical variable, etc

# Random factors are the classification variables that the unit of anlaysis is grouped under, i.e. these are
# typically the variables that define level 2, level 3, or level n. These factors can also be thought of as a
# population where the unit measures were randomly sampled from, i.e. (using the school example from above) the
# school (level 2) had a random sample of students (level 1) scores selected to be used in the study.

#######################################################################################################################

# Import the raw dataset:
raw_data = pd.read_csv("Total_Sat_Data.csv")

# Separate predictor and target variables:
Y = raw_data['TEP']
x = raw_data.drop('TEP', axis=1)  # Predictor array

#######################################################################################################################

# Visualize the categories effects as a boxplot:
boxplot = raw_data.boxplot(["TEP"], by=["Season"],
                           showmeans=True,
                           notch=True)

#######################################################################################################################

# CREATE A LINEAR MIXED EFFECTS MODEL USING THE ENTIRE DATA SET:

model = smf.mixedlm("TEP ~ Log_Chl + Temperature", raw_data, groups=raw_data["Season"])
mdf = model.fit()

print(mdf.summary())

#######################################################################################################################

# Checking model assumptions: Linear mixed effect models have the same assumptions as the traditional standard linear
# regression model

# -----------------------------
# Kernel density estimate plot:
fig = plt.figure(figsize=(16, 9))

ax = sns.distplot(mdf.resid, hist=False, kde_kws={"shade": True, "lw": 1}, fit=stats.norm)

ax.set_title("KDE Plot of Model Residuals (Blue) and Normal Distribution (Black)")
ax.set_xlabel("Residuals")

# -----------------------------
# QQ plot:
fig = plt.figure(figsize=(16, 9))
ax = fig.add_subplot(111)

sm.qqplot(mdf.resid, dist=stats.norm, line='s', ax=ax)
ax.set_title("Q-Q Plot")

# -----------------------------
# Test for normality with a Shapiro Wilks test:
labels = ["Statistic", "p-value"]
norm_res = stats.shapiro(mdf.resid)

for key, val in dict(zip(labels, norm_res)).items():
    print(key, val)

# -----------------------------
# Check residual variance: Residuals vs fitted values:
fig = plt.figure(figsize=(16, 9))

ax = sns.scatterplot(y=mdf.resid, x=mdf.fittedvalues)

ax.set_title("RVF Plot")
ax.set_xlabel("Fitted Values")
ax.set_ylabel("Residuals")

# Different view:
fig = plt.figure(figsize=(16, 9))

ax = sns.boxplot(x=mdf.model.groups, y=mdf.resid)

ax.set_title("Distribution of Residuals for Weight by Season")
ax.set_ylabel("Residuals")
ax.set_xlabel("Season")

# Formally test for homoskedasticity of the variance in residuals:
het_white_res = het_white(mdf.resid, mdf.model.exog)

labels = ["LM Statistic", "LM-Test p-value", "F-Statistic", "F-Test p-value"]

for key, val in dict(zip(labels, het_white_res)).items():
    print(key, val)

#######################################################################################################################

# EVALUATING AND CROSS VALIDATING THE MODEL

# Splitting the data: Training and validation:
x_train, x_test, y_train, y_test = train_test_split(x, Y, test_size=0.2, random_state=291)  # 291

# Make predictions on the testing sets:
y_prediction = mdf.predict(x_test)

# Make predictions for the training set for reference later:
y_train_prediction = mdf.predict(x_train)

# Use r2_score from sklearn: Closely related ot MSE
score = r2_score(y_test, y_prediction)

print('r2 score is', score)
print('mean_sqrd_error is==', mean_squared_error(y_test, y_prediction))
print('root_mean_squared error is==', np.sqrt(mean_squared_error(y_test, y_prediction)))

# Plot the results of the cross validation:
plt.axes(aspect='equal')
plt.scatter(y_prediction, y_test)  # plot the validation results
plt.scatter(y_train_prediction, y_train, alpha=0.5)  # visualize the training aspects of the model alongside the validation results
plt.xlabel('True Values [TEP]')
plt.ylabel('Predictions [TEP]')
lims = [0, 150]
plt.xlim(lims)
plt.ylim(lims)
_ = plt.plot(lims, lims)  # Add a 1:1 line through the graph for comparison