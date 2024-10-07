# -*- coding: utf-8 -*-
"""Copulas.ipynb

Automatically generated by Colab.

Original file is located at
    https://colab.research.google.com/drive/1NCCS1EHo7r0IPOjtN5311xlVo3Kq03D6

##Python
<center>

## Copulas For Dependencies Modeling

[Sudip Khadka](https://sudkc37.github.io/-Sudip_Khadka/)

</center>

Understanding financial market dependencies during extreme fluctuations is vital for effective risk management, diversification, and pricing. Copula co-movements reveal how shocks in one market can influence others, making it essential to evaluate co-movements, tail dependencies, and volatility spillovers. Analyzing asset dependencies within a portfolio is crucial for accurate risk assessment, as the portfolio's return distribution depends on both individual asset returns and their interdependencies.

Harry Markowitz's Modern Portfolio Theory (MPT), emphasized diversification and the risk-return relationship, introducing the covariance matrix. However, MPT's assumption of normally distributed returns does not capture the complex dependencies in financial markets, leading to the adoption of copulas.

Copulas models joint distributions while allowing for individual marginal distributions, providing deeper insights into portfolio risk. Copulas, such as Gaussian, t-copula, Vine and Clayton, are selected based on data characteristics and modeling requirements, with parameters optimized using maximum likelihood estimation.

Suppose that X and Y are real-valued random variables with joint distribution function 𝐹(𝑋,𝑌) and marginal distribution functions 𝐹𝑋 and 𝐹𝑌. We say that X and Y admit the copula C if 𝐶(𝐹𝑋 (𝑥), 𝐹𝑌 (𝑦))=𝐹(𝑋, 𝑌)(𝑥 ,𝑦) for all 𝑥 ,𝑦 ∈ 𝑅.
"""

!pip install copulas

import pandas as pd
import numpy as np
import yfinance as yf
import matplotlib.pyplot as plt
import datetime as dt
import seaborn as sns
from scipy.stats import norm
from scipy.stats import t,  beta
from warnings import filterwarnings
filterwarnings('ignore')
from scipy.stats import cauchy
from itertools import combinations
from statsmodels.distributions.empirical_distribution import ECDF
from copulas.multivariate import GaussianMultivariate
from mpl_toolkits.mplot3d import Axes3D
from copulas.bivariate import Clayton
from copulas.multivariate import VineCopula

#we are taking 6 year worth of historic data

end_date = dt.datetime.now()
start_date = end_date - dt.timedelta(days=365*6)

"""**Assets**

Biotechnology Index: Nasdaq Biotechnology Index (^NBI)

Technology Index : Nasdaq Composite (^IXIC)

Technology : S&P 500 (^GSPC)

Small-Cap Index: Russell 2000 (^RUT)

Sector-Agnostic Index: Dow Jone (^DJI)

CryptoCurrency : Bitcoin (BTC-USD)

"""

tickers =['^NBI','^IXIC','^GSPC','^RUT', 'BTC-USD','^DJI']

quotes = pd.DataFrame()
for ticker in tickers:
  quotes[ticker] = yf.download(ticker, start_date, end_date)['Adj Close']

quotes = quotes.dropna()
quotes

log_return = np.log(quotes/quotes.shift(1)).dropna()

plt.figure(figsize=(18, 10))
plt.plot(np.log(quotes))
plt.title('Log Returns')
plt.xlabel('Date')
plt.ylabel('Log Return')
plt.legend(tickers)
plt.show()

cols = 3
col = quotes.columns
feature_count = len(col)
rows = (feature_count + cols -1)//cols
fig, axes = plt.subplots(rows, cols, figsize=(17, 5*rows))
axes = axes.flatten()

for i, ax in zip(col, axes):
  sns.histplot(log_return[i], ax=ax, bins=40, kde=True)
  ax.set_title(i)
  ax.set_xlabel(i)
  ax.set_ylabel('Frequency')
for ax in axes[feature_count:]:
  ax.axis('off')
plt.tight_layout()
plt.show()

Skewness =  log_return.skew()
Kurtosis = log_return.kurt()
mean = log_return.mean()
std = log_return.std()
pd.DataFrame({'Skewness': Skewness, 'Kurtosis': Kurtosis, 'Mean': mean, 'Standard Deviation': std})

"""We employed four different distributions—Normal, Student-t, Beta, and Cauchy—to gain insights into the underlying nature of the assets.

The normal distribution is characterized by its symmetry and bell-shaped curve. It is given by:
$$
\\f(x|\mu,\sigma^2) = \frac{{1}}{√2\pi\sigma^2}\exp^ - (\frac{x-\mu}{2\sigma^2})
$$

The Student's t distribution is symmetric and bell-shaped, like the normal distribution, but has heavier tails, making it suitable for smaller sample sizes where normality assumptions may not hold. It is given by:
$$
\\f(x|v) = \frac{\Gamma(\frac{v+1}{2})}{√v\pi\,\Gamma(\frac{v}{2})}\left[1 + \frac{x^2}{\nu}\right]^{-\frac{\nu+1}{2}}
$$
*where,
v is degree of freedom*


The beta distribution is  defined on the interval [0, 1], characterized by its two shape parameters, which allow it to model a variety of shapes including uniform, U-shaped, and bell-shaped distributions.
$$
\\f(x|α,β) = \frac{x^{\alpha-1}(1-x)^{\beta-1}}{Β(\alpha,\beta)}
$$
*where, B is normalized constant*

The Cauchy distribution is characterized by its location parameter (median) and scale parameter, known for its heavy tails and undefined mean and variance.
$$
\\f(x|x_0,γ) = \frac{1}{\pi\gamma[1+ (\frac{x-x_0}{\gamma})^2]}
$$
*where, x_0 is the location parameter (median), and
γ is the scale parameter*
"""

cols = 3
col = quotes.columns
feature_count = len(col)
rows = (feature_count + cols - 1) // cols
fig, axes = plt.subplots(rows, cols, figsize=(17, 5 * rows))
axes = axes.flatten()

for i, ax in zip(col, axes):
  #normal
    mean = np.mean(log_return[i])
    std = np.std(log_return[i])

    #T
    params_t = t.fit(log_return[i])
    df, t_loc, t_scale = params_t[0], params_t[1], params_t[2]

  #Beta
    params_beta = beta.fit(log_return[i])
    a, b, loc, scale = params_beta[0], params_beta[1], params_beta[2], params_beta[3]

  #Cauchy
    ca_loc, ca_scale = cauchy.fit(log_return[i])

    x = np.linspace(min(log_return[i]), max(log_return[i]), 100)

    ax.hist(log_return[i], bins=100, density=True, alpha=0.5, label='Original')

    ax.plot(x, norm.pdf(x, mean, std), color='red', label='Normal Distribution')
    ax.plot(x, t.pdf(x, df, t_loc, t_scale), color='green', label='t-Distribution')
    ax.plot(x, beta.pdf(x, a, b, loc, scale), color='orange', label='Beta Distribution')

    ax.plot(x, cauchy.pdf(x, ca_loc, ca_scale), color='purple', label='Cauchy Distribution')

    ax.legend()
    ax.set_title(i)
    ax.set_xlabel(i)
    ax.set_ylabel('Frequency')

for ax in axes[feature_count:]:
    ax.axis('off')

plt.tight_layout()
plt.show()

log_return.corr()

"""Now we will focus on tail dependency, a concept in statistics and probability theory that describes the extent of dependence in the extreme values (tails) of two or more random variables. It measures the likelihood that extreme values in one variable will be accompanied by extreme values in another. In the context of financial markets, tail dependence might measure the probability that an extreme loss in one stock is accompanied by an extreme loss in another stock.
Upper tail shows the co-occurrence of extreme high values, while lower tail shows the co-occurrence of extreme low values.
"""

variables = list(quotes.columns)
pairs = list(combinations(variables,2))
fig, axes = plt.subplots(5, 3, figsize=(16,18))
axes = axes.flatten()

for i, (var1, var2) in enumerate(pairs):

  lower_tail_threshold = np.percentile(log_return[var1], 1)
  lower_extreme_indices = np.where(log_return[var1] <= lower_tail_threshold)
  upper_tail_threshold = np.percentile(log_return[var1], 99)
  upper_extreme_indices = np.where(log_return[var1] >= upper_tail_threshold)

  axes[i].scatter(log_return[var1].iloc[lower_extreme_indices], log_return[var2].iloc[lower_extreme_indices], color='red', label='Lower Tail Dependence')
  axes[i].scatter(log_return[var1].iloc[upper_extreme_indices], log_return[var2].iloc[upper_extreme_indices], color='green', label='Upper Tail Dependence')


  axes[i].scatter(log_return[var1], log_return[var2], alpha=0.5)
  axes[i].set_xlabel(var1)
  axes[i].set_ylabel(var2)
  axes[i].set_title(f'{var1} vs {var2}')
  axes[i].legend()

plt.tight_layout()
plt.show()

"""To make it easier to analyze, we use the cumulative distribution functions (CDFs) of the returns instead of the raw data. This removes the individual characteristics of each return series."""

log_return_cdf = log_return.apply(lambda col:ECDF(col))
transcdf = log_return.apply(lambda col:log_return_cdf[col.name](col))

transcdf

variabes = list(quotes.columns)
pairs = list(combinations(variabes,2))
fig, axes = plt.subplots(5, 3, figsize=(16,18))
axes = axes.flatten()

for i, (var1, var2) in enumerate(pairs):
  axes[i].scatter(transcdf[var1], transcdf[var2], alpha=0.4)
  axes[i].set_xlabel(var1)
  axes[i].set_ylabel(var2)
  axes[i].set_title(f'{var1} vs {var2}')

plt.tight_layout()
plt.show()

"""We will now fit several copulas to our data to identify the most appropriate one that explains the relationship between the variables. All copulas are inherently fitted on the cumulative distribution function (CDF), we have transformed the data into the CDF format for this purpose.By transforming our data into the CDF, we ensure that the copulas are fitted correctly, as copulas are defined in the context of uniform marginals.

#Gaussian Copula

Gaussian Copula models the dependence between multiple variables, allowing for the correlation of variables whose marginal distributions may not be normally distributed. It is given by:

$$
\\C_R(\vec{u}) = \phi_R(\phi^{-1}(u_1),....,\phi^{-1}(u_n)
$$

where,

C_R represents the Gaussian copula with correlation matrix R

u_1,..., u_n are the uniform marginals of the variables, derived from their cumulative distribution functions (CDFs)

𝜙_R is the CDF of the multivariate normal distribution with correlation matrix R and zero mean

𝜙^ -1 denotes the inverse of the standard normal CDF.
"""

copula = GaussianMultivariate()
copula.fit(transcdf)

synthetic_data = copula.sample(len(transcdf))

"""To determine if the Gaussian copula can effectively explain the relationship between variables, we are plotting both the simulated samples and the actual observations. From the scatter plot, we observe that the Gaussian copula closely matches the real observations. Additionally, the 3-D plots also further demonstrate a good approximation of the data."""

def plotter(df):
  variables = list(quotes.columns)
  pairs = list(combinations(variables, 2))
  fig, axes = plt.subplots(5,3, figsize=(14,18))
  axes = axes.flatten()

  for i, (var1, var2) in enumerate(pairs):
    axes[i].scatter(df[var1], df[var2], label ='Simulated', alpha=0.4)
    axes[i].scatter(transcdf[var1], transcdf[var2], label ='Original', alpha=0.2)
    axes[i].set_xlabel(var1)
    axes[i].set_ylabel(var2)
    axes[i].set_title(f'{var1} vs {var2}')
    axes[i].legend()

  plt.tight_layout()
  plt.show()

plotter(synthetic_data)

copula.correlation

def plotter_3d(df):
    variables = list(df.columns)
    pairs = list(combinations(variables, 3))
    fig, axes = plt.subplots(5, 4, figsize=(16, 22), subplot_kw={'projection': '3d'})
    axes = axes.flatten()

    for i, (var1, var2, var3) in enumerate(pairs):
        axes[i].scatter(df[var1], df[var2], df[var3], label='Simulated', alpha=0.4)
        axes[i].scatter(transcdf[var1], transcdf[var2], transcdf[var3], label='Original', alpha=0.4)
        axes[i].set_xlabel(var1)
        axes[i].set_ylabel(var2)
        axes[i].set_zlabel(var3)
        axes[i].set_title(f'{var1} vs {var2} vs {var3}')
        axes[i].legend()

    plt.tight_layout()
    plt.show()


plotter_3d(synthetic_data)

"""# VineCopula

A vine copula is a type of hierarchical copula structure used to model multivariate dependencies among random variables. It's particularly useful when the variables exhibit complex dependencies that are challenging to model with simpler copula structures like the Gaussian copula. It organize the joint distribution of variables into a hierarchical tree-like structure. This structure helps in capturing complex dependencies by breaking them down into more manageable conditional relationships. We have modeled three types of Vine copula which are Vine Direct, Vine Regular and Vine Central.

<br/>

**D-Vine Copula**

The structure of a D-vine is such that each variable is connected sequentially, forming a "path" through the variables. Their dependencies are modeled between adjacent variables in the first tree. The joint density of the continuously distributed random vector X can be written in terms of conditional bivariate copula densities and its marginal densities. Given a set of
n variables {U_1, ....U_n} with a copula density C, the D-vine copula density can be written as:
$$
\\C(\vec{u}) = \prod_{i=1}^{n-1} \prod_{j=1}^{n-1} c_{j, j+i; v_{j+1}:j+i-1} (F_{j|v_{j+1: j+i-1}}(u_j), F_{j+i|v_{j+1:j+i-1}}(U_{j+1}))
$$

where,
$
[
c_{j, j+i; \mathbf{v}_{j+1:j+i-1}} \text{ denotes the bivariate copula density for the pair } (U_j, U_{j+i}) \text{ conditioned on the intermediate variables } \mathbf{v}_{j+1:j+i-1}
]
$

$
[
F_{j|v_{j+1: j+i-1}} \text{is the conditional distribution function of} (U_j) \text{given the intermediate variables.}
]
$
"""

#Vine-d
vine_d = VineCopula('direct')
vine_d.fit(transcdf)

trees = vine_d.trees
for i, tree in enumerate(trees):
    print(f"Tree {i+1}:")
    print(tree)

"""To interpret the structure of the vine copula trees, we need to understand the notation used and how vine copulas are structured. The output we have is from a vine copula model, and it describes the pair-copulas at each level (tree) of the vine structure. K Indicates
k-th tree in the vine structure. L and R are the left and right nodes of the pair-copula. D is the conditioning set (variables that condition the copula relationship between L and R).
Copula is he type of copula used for the pair and the theta is the parameter of the copula, indicating the strength and direction of dependence.

**Note: The explainability of vine-c, vine-d and vine-r copulas remains consistent. Their distinction lies in the structure of the tree and connected nodes.**

**Tree1:**

L:3 R:4 explains that A Frank copula between variable 3 and variable 4 with no conditioning set where theta of 1.65 indicates moderate positive dependence.

L:3 R:4 explains Frank copula between variable 0 and variable 1 with no conditioning set where theta 5.79 indicates strong positive dependence.

Simillarly, L:0 R:1, L:1 R:2, L:2 R:5 have the similar interpretability as the theta value is directly proportion to the strong positive dependency.

**Tree2:**

L:0 R:4 explains a Gumbel copula between variable 0 and variable 4, conditioned on variable 3 where theta = 1.02 indicates very weak positive dependence.

L:1 R:3 have similay intepretability as tree 1 Frank copula.

L:0 R:2 explains clayton copula between variable 0 and variable 2, conditioned on variable 1 where theta = 0.08 indicates very weak positive dependence.

Furthermore, we use the aforementioned dependency parameters to simulate and compare with the original data, in order to evaluate whether the model accurately explains the dependencies
"""

vine_d_samples = vine_d.sample(len(transcdf))

plotter(vine_d_samples)

plotter_3d(vine_d_samples)

"""**C-Vine Copula**

In a C-vine, one central node is connected to all other variables in the first tree, and the dependencies between pairs of variables are modeled conditionally on this central variable. The C-vine structure is useful for modeling situations where root has a dominant influence over all other variables, and dependencies between other variables can be structured around this dominant variable. Given a set of
n variables {U_1, ....U_n} with a copula density C, the D-vine copula density can be written as:

$$
\\C(\vec{u}) = \prod_{i=1}^{n-1} \prod_{j=1}^{n-i} c_{j, j+i; 1: j-1} (F_{j|1:i-1}(u_j|u_1,...,u_{j-1}), F_{j+i|1:j-1}(U_{j+i}|u_1,...,u_{j-1}))
$$

where,

$
c_{j, j+i; 1: j-1}\text{denotes the bivariate copula density for the pair}(u_j, u_{j+i})\text{conditioned on the variables}(u_1,....,u_{j-1})
$

$
F_{j|1:i-1}\text{is the conditional distribution function of}(u_j)\text{given the variables }(u_1,....,u_{j-1})
$
"""

#Vine-c
vine_c = VineCopula('center')
vine_c.fit(transcdf)

trees = vine_c.trees
for i, tree in enumerate(trees):
    print(f"Tree {i+1}:")
    print(tree)

vine_c_samples = vine_c.sample(len(transcdf))

plotter(vine_c_samples)

plotter_3d(vine_c_samples)

"""**R-Vine Copula**

The R-vine structure allows for modeling complex dependencies between variables by sequentially building the dependency structure tree by tree. R-vines are the most flexible, allowing for any pair-copula construction  where the trees can have any structure, as long as they adhere to the vine copula's rules. This hierarchical approach can capture intricate dependency patterns.Given a set of
n variables {U_1, ....U_n} with a copula density C, the D-vine copula density can be written as:

$$
\\C(\vec{u}) = \prod_{i=1}^{n-1} \prod_{j=1}^{n-k} c_{j(i,k),k(i,k);D(i,k)} (F_{j(i,k)|D(i,k)}(u_{j(i,k)}|u_{D(i,k)}), F_{k(i,k)|D(i,k)}(u_{k(i,k)}|u_{D(i,k)}))
$$

where,
$
[
c_{j(i,k),k(i,k);D(i,k)} \text{ denotes the bivariate copula density for the pair } (U_{j(i,k)}, U_{k(i,k)}) \text{ conditioned on the intermediate variables }D(i,k)
]
$

$
[
F_{j(i,k)|D(i,k)} \text{is the conditional distribution function of} (U_{j(i,k)}) \text{given the variables in} D(i,k)
]
$

$
j(i,k),\,k(i,k)\text{are indices representing the variables involved in the k-th tree.}
$

$
D(i,k)\text{is the set of conditioning variables for the bivariate copula in the k-th tree.}
$
"""

#Vine-r
vine_r = VineCopula('regular')
vine_r.fit(transcdf)

trees = vine_r.trees
for i, tree in enumerate(trees):
    print(f"Tree {i+1}:")
    print(tree)

vine_r_samples = vine_r.sample(len(transcdf))
plotter(vine_r_samples)

plotter_3d(vine_r_samples)

"""# Clayton Copula

Clayton Copula model dependence that is skewed towards the lower end of the distribution. It is given by:

$$
\\C_θ(\vec{u}) = (\sum_{i=1}^{n} (u_i^{-θ})-n+1)^{\frac{-1}{θ}}
$$
"""

def Clayton_copula(df):
    clayton = Clayton()

    variables = list(df.columns)
    pairs = list(combinations(variables, 2))
    for var1, var2 in pairs:
        transcdf_1 = df[[var1, var2]].to_numpy()

        clayton.fit(transcdf_1)

        clayton_samples = clayton.sample(len(transcdf_1))

    return df

Clayton_copula_sample = Clayton_copula(transcdf)
Clayton_copula_sample.head()

def plot_clayton_copula(df):
    clayton = Clayton()

    variables = list(df.columns)
    pairs = list(combinations(variables, 2))

    fig, axes = plt.subplots(5, 3, figsize=(16, 22))
    axes = axes.flatten()

    for i, (var1, var2) in enumerate(pairs):
        transcdf_1 = df[[var1, var2]].to_numpy()

        clayton.fit(transcdf_1)

        clayton_samples = clayton.sample(len(transcdf_1))

        axes[i].scatter(transcdf_1[:, 0], transcdf_1[:, 1], label='Original', alpha=0.4)
        axes[i].scatter(clayton_samples[:, 0], clayton_samples[:, 1], label='Clayton Copula', alpha=0.4)
        axes[i].set_xlabel(var1)
        axes[i].set_ylabel(var2)
        axes[i].set_title(f'{var1} vs {var2}')
        axes[i].legend()

    plt.tight_layout()
    plt.show()
plot_clayton_copula(transcdf)

"""# VaR"""

portfolio_value  = 500000
investment_per_asset = portfolio_value / len(quotes)

equally_weg = [investment_per_asset/quotes for quotes in quotes.iloc[-1]]

pd.DataFrame({'Price': quotes.iloc[-1],
              'Shares':equally_weg})

#Covariance Method
cov_sample_return = (log_return * equally_weg).sum(axis=1)

Gaussian = synthetic_data
Vine_d = vine_d_samples
Vine_c = vine_c_samples
Vine_r = vine_r_samples
Clayton = Clayton_copula_sample
Covariance = cov_sample_return

model_names = ['Gaussian', 'Clayton', 'Vine_d', 'Vine_c', 'Vine_r']

confidence_interval = 0.99
window = 5
portfolio_value = 100000
var = []
all_range_return = []

for model_name in model_names:
    marginals = [norm.fit(log_return[asset]) for asset in log_return.columns]
    simulated_returns = np.array([norm.ppf(eval(model_name).iloc[:,j], *marginals[j]) for j in range(len(log_return.columns))]).T
    simulated_portfolio_returns = np.sum(simulated_returns * equally_weg, axis=1)
    simulated_portfolio_returns = pd.Series(simulated_portfolio_returns)

    range_return = simulated_portfolio_returns.rolling(window=window).sum().dropna()  # period
    all_range_return.append(range_return)

    VaR = np.percentile(range_return, 100-(1-confidence_interval)*100)*portfolio_value
    var.append(VaR)
    print(f'{model_name} VaR at {confidence_interval:.0%} confidence level is $ {VaR:.2f}')

plt.figure(figsize=(16, 8))
plt.hist(all_range_return[0]*portfolio_value, bins=60, density=True)
sns.kdeplot(all_range_return[0]*portfolio_value, bw_adjust=0.5, color='blue')
colors = ['red', 'green', 'blue', 'purple', 'orange']
for idx, VaR in enumerate(var):
    color = colors[idx % len(colors)]
    plt.axvline(-VaR, linestyle='dashed', color=color, label=f'{model_names[idx]}')
#Covariance mathod
cov_sample_return = (log_return * equally_weg).sum(axis=1)
range_return = cov_sample_return.rolling(window=window).sum().dropna()
VaR_1 = np.percentile(range_return, 100 - (1 - confidence_interval) * 100)* portfolio_value
print(f'Covariance VaR at {confidence_interval:.0%} confidence level is $ {VaR_1:.2f}')
plt.axvline(-VaR_1, linestyle='dashed', label=f'Covariance')

plt.ylabel('Density')
plt.xlabel(f'{window}-Day Portfolio Return (Dollar Value)')
plt.title(f'Distribution of Portfolio {window}-Day Rolling window (Dollar Value) at {confidence_interval:.0%} confidence level')
plt.legend()
plt.show()

"""#Conclusion


The Gaussian and Clayton Copulas are effective tools for explaining dependency and associated Value at Risk (VaR) in financial time series data, such as stock prices. The Clayton Copula, in particular, excels in assessing risk under extreme market conditions. This is because the Clayton Copula captures lower tail dependency effectively, which is crucial in financial markets where extreme losses are of significant concern.

Our simulation revealed that the Clayton distribution is particularly adept at capturing this lower tail dependency, making it a valuable tool for stress testing and risk management. On the other hand, the Vine Copula, despite its potential, did not perform well in our analysis of financial time series data. This could be due to the complexity and high-dimensional nature of Vine Copulas, which may require more sophisticated estimation techniques and larger sample sizes to perform optimally.

The covariance method, while useful for measuring linear relationships between variables, does not capture true dependency during extreme market situations. Covariance assumes a normal distribution and fails to account for the heavy tails and skewness often observed in financial time series data. Therefore, it is less effective in risk management scenarios where understanding tail dependency is critical.
"""

!jupyter nbconvert --to html /content/Copulas-5.ipynb
