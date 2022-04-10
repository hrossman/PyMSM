---
title: 'PyMSM: Python package for Competing Risks and Multi-state models for Survival Data'
tags:
  - Python
  - multistate models
  - survival analysis
  - competing risks
authors:
  - name: Hagai Rossman^[Co-first author] # note this makes a footnote saying 'Co-first author'
    orcid: 0000-0000-0000-0000
    affiliation: 1 # (Multiple affiliations must be quoted)
  - name: Ayya Keshet^
    orcid: 0000-0000-0000-0000
    affiliation: 1 # (Multiple affiliations must be quoted)
  - name: Maka Gorfine^[Corresponding author]
    affiliation: 2
affiliations:
 - name: Department of Computer Science and Applied Mathematics, Weizmann Institute of Science, Rehovot, Israel
   index: 1
 - name: Department of Statistics and Operations Research, Tel Aviv University, Tel Aviv, Israel
   index: 2
date: 10 April 2022
bibliography: paper.bib
---

# Summary
Multi-state data are common, and could be used to describe trajectories in diverse applications such as a patient's health progression through disease states, a taxi drivers passenger pickups or a website browsing trajectory to name a few. 
When faced with such data, a researcher or clinician might seek to characterize the possible transitions between states, their occurrence probabilities, or to predict the trajectory of future patients - all conditioned on various baseline and time-varying individual covariates. By fitting a multi-state model, we can learn the hazard for each specific transition, which would later be used to predict future paths. Predicting paths could be used at a single patient level, for example predict how long until a cancer patient will be relapse-free given his current health status, or at what probability will a patient end a trajectory at any of the possible states; and at the population level, for example predicting how many patients which arrive at the emergency-room will need to be admitted, given their covariates.


# Statement of need

`PyMSM` is a Python package for fitting multi-state models, with a simple API which allows user-defined models, predictions at a single or population sample level, and various statistical summaries and figures.
Features of this software include:
- Fitting a Competing risks Multistate model based on various types of survival analysis (time-to-event) such as Cox proportional hazards models or machine learning models, while taking into account right censoring, competing events, recurrent events, left truncation, and time-dependent covariates.
- Running Monte-carlo simulations (in parallel computation) for paths emitted by the trained model and extracting various summary statistics and plots.
- Loading or configuring a pre-defined model and generating simulated data in terms of random paths using model parameters, which could be highly useful as a research tool.
-  Modularity and compatibility for different time-to-event models such as Survival Forests and other custom ML models provided by the user.

The package is designed to allow modular usage by both experienced researchers and non-expert users. In addition to fitting a multi-state model for a given data - `PyMSM` allows the user to simulate trajectories, thus creating a multi-state data-set, from a predefined model. This could be a valuable research tool - both for sharing sensitive simulated individual data and as a tool for any downstream task which needs individual trajectories.
To the authors best knowledge, this is the first open-source multi-state model tool that allows fitting of such models while also dealing with important concepts such as right censoring, competing events, recurrent events, left truncation, and time-dependent covariates.

# Usage examples
This project is based on methods first introduced during 2020 for predicting national COVID-19 hospitalizations in Israel. Important health policy applications based on these methods were built and used by government policymakers throughout the pandemic. For example:  
- Help assess hospital resource utilization [@Roimi:2021].  
- Associations between high hospital load and excess deaths [@Rossman:2021].  
 
A similar R version of this package is available in [@Roimi:2021], yet this is the first Python version to be released as an open-source package containing extended features and use cases.
Other usage examples are provided in the software package docs such as breast cancer state transitions (Rotterdam dataset), AIDs competing risk data, disease stage data from the European Society for Blood and Marrow Transplantation (EBMT) and COVID-19 national hospitalizations.


# The PyMSM package

A brief overview of the package functionality is described below. Detailed explanations of the API, along with four full usage examples on real data are available in the package documentation at https://hrossman.github.io/pymsm/.


## Model fitting
Fitting a multi-state model to a data-set requires only a few simple steps:  
- Preparing a data-set in one of two formats  
- Defining a function for updating time-dependent covariates  
- Define covariate columns  
- Define terminal states  
- Define a minimum number of data transitions needed to fit a transition  
Once all the above was done, the user can fit a multi-state model to his data-set, and use it for downstream analyses.

## Path sampling
Using the previously fitted multi-state model, the user can sample paths using the Monte Carlo simulations. Providing covariates, initial state and time - next states are sequentially sampled via the model parameters, and the process concludes when the patient arrives at a terminal state or the number of transitions exceeds the specified maximum. With the sampled paths, the user can explore statistics such as the probability of being in any of the states or the time spent in each state.

## Costume fitters
`PyMSM` allows configuration of custom event-specific-fitters.
EventSpecificFitter class is an abstract class which defines the API which needs to be implemented by the user.

Some custom fitters are available off-the-shelf such as Survival trees (Ishwaran 2008).

## Simulating Multi-state Survival Data
Using a pre-loaded or a pre-defined model, {PyMSM} provides an API to generate simulated data of random trajectories using the model parameters. Creating a simulated multi-state paths data-set could serve as a useful research tool in cases where data sharing is limited due to privacy limitations, or as a generation tool for any downstream task which requires individual trajectories.

# Models and Methods
In this section we give an overview of the models and methods underlying the statistics and computations performed in `PyMSM`.

# Introduction
The description of the content of \texttt{PyMSM} would be easier to digest under a certain setting.  Thus, to set the stage, we adopt the multi-state model of [@Roimi:2021]. Specifically, assume a multi-state model consists of four states $A,B,C,D$ and six possible transitions:
$$
A \rightarrow B \,\,\,\,\,\,       A \rightarrow C   \,\,\,\,\,\,     A \rightarrow D   \,\,\,\,\,\,    B \rightarrow A \,\,\,\,\,\,    B \rightarrow D \,\,\,\,\,\,   C \rightarrow A \, .
$$
Each transition is characterizes by a transition-specific hazard function, also known as a cause-specific hazard function,
$$
\lambda_{A,B} (t|Z) \,\,\, \lambda_{A,C} (t|Z) \,\,\, 	\lambda_{A,D} (t|Z) \,\,\, \lambda_{B,A} (t|Z)  \,\,\, \lambda_{B,D} (t|Z) \,\,\,  \lambda_{C,A} (t|Z) \,
$$
for $t > 0$ and $Z$ vector of covariates. Although $Z$ is shared by the six models above,  it does not imply that identical covariates must be used in these models. For example, in Cox models with   transition-dependent   regression coefficient vectors,  one can set any specific coefficient to 0 for excluding  the corresponding covariate.  

Let $J_C$ and $J_N$ denote the current and next states, respectively, and $T$ denotes the transition time. Assume the journey of an observation in the system described by the multi-state model starts at state $j^*$ with vector of baseline covariates $W$. Let $Z(t)$ be a time-dependent vector of covariates, where
$$ 
Z(t) = (W^T,\widetilde{W}(t))
$$
and $\widetilde{W}(t)$ is a time-dependent vector of covariates known at the entrance to the new state. Let $K_{j^*}$ be the set of possible states that can be reached directly from state $j^*$. Then, the conditional probability of transition $j^* \rightarrow j$, $j \in K_{j^*}$, by time $t$ given $Z(0)=Z$ is given by
$$
\Pr(T \leq t, J_N=j|J_C=j^*,Z(0)=Z) = \int_0^t \lambda_{j^*,j}(u|Z)\exp\left\{-\sum_{k=1}^{|K_{j^*}|} \Lambda_{j^*,k}(u-|Z) \right\} du \, ,
$$
where $u-$ is a time  just prior to $u$, $|K_{j^*}|$ is the cardinality of $K_{j^*}$ and  $\Lambda_{j,k}(t|Z)=\int_0^t \lambda_{j,k}(u|Z) du$ is the cumulative hazard function. In our example, if the first state $j^*=A$, $K_{j^*}=\{B,C,D\}$, and 

$$
\Pr(T \leq t, J_N=j|J_C=A,Z(0)=Z) = 
$$  
$$
\int_0^t \lambda_{A,j}(u|Z)\exp\left\{- \Lambda_{A,B}(u-|Z) - \Lambda_{A,C}(u-|Z) - \Lambda_{A,D}(u-|Z)\right\} du \, ,
$$

The marginal probability of transition $j^* \rightarrow j$ is given by
$$
\Pr(J_N=j|J_C=j^*,Z(0)=Z) = \int_0^\infty \lambda_{j^*,j}(u|Z)\exp\left\{-\sum_{k=1}^{|K_{j^*}|} \Lambda_{j^*,k}(u-|Z) \right\} du \, ,
$$
and the probability of transition time less than $t$ given a transition $j^* \rightarrow j$
$$
\Pr(T \leq t | J_N=j,J_C=j^*, Z(0)=Z)
= \frac{ \int_0^t \lambda_{j^*,j}(u|Z)\exp\left\{-\sum_{k=1}^{|K_{j^*}|} \Lambda_{j^*,k}(u-|Z) \right\} du  }
{ \int_0^\infty \lambda_{j^*,j}(u|Z)\exp\left\{-\sum_{k=1}^{|K_{j^*}|} \Lambda_{j^*,k}(u-|Z) \right\} du  }  \, .
$$
Now assume an observation entered state $j'$ at time $t'>0$ with $Z(t')$. Then, the probability of $j' \rightarrow j$ by time $t$ is given by 
$$
\Pr(T \leq t, J_N=j|J_C=j',Z(t')=Z) = \int_{t'}^t \lambda_{j',j}(u|Z)\exp\left\{-\sum_{k=1}^{|K_{j'}|} \Lambda_{j',k}(u-|Z) \right\} du \, ,
$$
and
$$
\Pr(T \leq t| J_N=j,J_C=j',Z(t')=Z) = 
\frac{ \int_{t'}^t \lambda_{j',j}(u|Z)\exp\left\{-\sum_{k=1}^{|K_{j'}|} \Lambda_{j',k}(u-|Z) \right\} du }
{ \int_{t'}^\infty \lambda_{j',j}(u|Z)\exp\left\{-\sum_{k=1}^{|K_{j'}|} \Lambda_{j',k}(u-|Z) \right\} du } \, .
$$    
All the above, set the main multi-state model components required for prediction, as will be explained in the following sections.

# Estimation

## Cox transition-specific hazard models
The estimation procedure for the hazard functions that define the multi-state model can be chosen by the user. For example, if Cox models are  adopted, where each transition $j \rightarrow j'$ consists of transition-specific unspecified baseline hazard function $\lambda_{0j,j'}(\cdot)$ and a 
transition-specific vector of regression coefficients $\beta_{j,j'}$, i.e.,
$$
\lambda_{j,j'}(t|Z) = \lambda_{0j,j'}(t) \exp(Z^T \beta_{j,j'}) \, ,
$$
the estimation procedure is straightforward. Specifically, under transition-specific semi-parametric Cox models, we can easily deal with: 
- Right censoring and competing events based on the approach of (andersen1991non). Namely, maximization of the likelihood function in terms of all the involved  Cox models is done by maximizing the likelihood of each transition separately. Thus, we use the standard partial likelihood estimators of $\beta_{j,j'}$ (klein2006survival) and Breslow estimator of $\Lambda_{0j,j'}(t)=\int_0^t \lambda_{0j,j'}(u)du$ (Breslow, 1972). 
- Left truncation which occurs at each transition that is not the origin state of the subject's path. Bias due to left truncation is eliminated by using the well-known risk-set correction (klein2006survival). 
- Recurrent events which occurs when subjects visit the same state multiple times. In such cases, the robust standard errors account for correlated outcomes within a subject (andersen1982cox). 	

Based on the estimates of the regression coefficients and the cumulative baseline hazard functions all the distribution functions of Section \ref{Sec1} can be estimated by replacing the integrals with sums over the observed failure time, and any unknown parameter is replaced by its estimator. Specifically, let $\tau_{j^*,j}$ be the largest observed event time of transition $j^* \rightarrow j$. Then, 
$$
\widehat{\Pr} (J_N=j | J_C=j^*,Z(0)=Z) \\
=   \sum_{t_m \leq \tau_{j^*,j}} \exp\left( \widehat\beta_{j^*,j}^T Z\right) \widehat\lambda_{0j^*,j}(t_m) \exp \left\{-\sum_{k=1}^{|K_{j^*}|} \widehat\Lambda_{0j^*,k}(t_{m-1})\exp\left( \widehat\beta_{j^*,k}^T Z\right) \right\} \, ,  
$$

$$
\widehat{\Pr} (T\leq t| J_N=j', J_C=j^* , Z(0)=Z)\\
\hspace{0.5cm} = \frac{\sum_{t_m \leq t} \exp\left( \widehat\beta_{j^*,j'}^T Z\right) \widehat\lambda_{0j^*,j'}(t_m) \exp \left\{-\sum_{k=1}^{|K_{j^*}|} \widehat\Lambda_{0j^*,k}(t_{m-1})\exp\left( \widehat\beta_{j^*k}^T Z\right) \right\} }{ \sum_{t_m \leq \tau_{j^*,j'}} \exp\left( \widehat\beta_{j^*,j'}^T Z\right) \widehat\lambda_{0j^*,j'}(t_m) \exp \left\{-\sum_{k=1}^{K_{j^*}} \widehat\Lambda_{0j^*,k}(t_{m-1})\exp\left( \widehat\beta_{j^*,k}^T Z\right) \right\} } \, , 
$$
and finally, given a new $\breve{j}$, the estimated probability of staying at state $j'$ less than or equal $t$ time unit is given by
$$
\widehat{\Pr} (T\leq t| J_N=\breve{j}, J_C=j' , Z(t')=Z) \\
\hspace{0.5cm} = \frac{\sum_{t' < t_m \leq t} \exp\left( \widehat\beta_{j',\breve{j}}^T Z\right) \widehat\lambda_{0j',\breve{j}}(t_m) \exp \left\{-\sum_{k=1}^{|K_{j'}|} \widehat\Lambda_{0j',k}(t_{m-1})\exp\left( \widehat\beta_{j',k}^T Z\right) \right\} }{ \sum_{t' < t_m \leq \tau_{j',\breve{j}}} \exp\left( \widehat\beta_{j',\breve{j}}^T Z\right) \widehat\lambda_{0j',\breve{j}}(t_m) \exp \left\{-\sum_{k=1}^{K_{j'}} \widehat\Lambda_{0j',k}(t_{m-1})\exp\left( \widehat\beta_{j',k}^T Z\right) \right\} } \, .
$$

# Other transition-specific models
Similarly, the user can define other survival models and estimation procedure, such as accelerated failure time model, random survival forests (ref) etc, for each transition, as explained in section XXXCustomeFitters.

# Prediction - Monte Carlo Simulation
Based on the multi-state model, we reconstruct the complete distribution of the path for a new observation, given the observed covariates $W$. Based on the reconstructed distribution we estimate
- The probability of visiting each state.
- The total length of stay at each state.
- The total length of stay in the entire system.

The above quantities can be predicted before entering the system and also during the stay at one of the systems' states, while correctly taking into account the accumulated time already spent in the system and $Z(\cdot)$.

We reconstruct the distribution of the path for a new observation by Monte-Carlo simulation. Assume the starting state (provided by the user) is $j^*$. Then, the next state $J_N$ is sampled based on the discrete conditional probabilities
$$
p_{j|j^*,Z}= \frac{\widehat{\Pr} (J_N=j | J_C=j^*, Z(0)=Z) }{\sum_{j'=1}^{K_{j^*}} \widehat{\Pr} (J_N=j' | J_C=j^*, Z(0)=Z)}  \, .
$$
where $j \in K_{j^*}$ and the summation is over the distinct observed event times of transition $j^* \rightarrow j$. Once we sampled the next state, denoted by $j'$, the time to be spent at state $j^*$ is sampled based on 
$$
\widehat{\Pr} (T\leq t| J_N=j', J_C=j^* , Z(0)=Z) \, .
$$
This is done by sampling $U \sim Uniform[0,1]$, equating 
$$
U=\widehat{\Pr} (T\leq t| J_N=j', J_C=j^* , Z(0)=Z)
$$ 
and solving for $t$. Denote the sampled time by $t'$ and update $Z(t')$. In case $j'$, is a terminal state, the sampling path ends here. Otherwise, the current state is updated to $J_C=j'$, and the following state is sampled by $p_{j|j',Z(t')}$, $j=1 \in  K_{j'}$, 
$$
p_{`j|j',Z}= \frac{\sum_{t' < t_m \leq \tau_{j',j}} \exp\left( \widehat\beta_{j',j}^T Z\right) \widehat\lambda_{0j',j}(t_m) \exp \left\{-\sum_{k=1}^{|K_{j'}|} \widehat\Lambda_{0j',k}(t_{m-1})\exp\left( \widehat\beta_{j',k}^T Z\right) \right\} }
{\sum_{j^{**}=1}^{K_{j'}} \sum_{t' < t_m \leq \tau_{j',j^{**}}} \exp\left( \widehat\beta_{j',j^{**}}^T Z\right) \widehat\lambda_{0j',j^{**}}(t_m) \exp \left\{-\sum_{k=1}^{|K_{j'}|} \widehat\Lambda_{0j',k}(t_{m-1})\exp\left( \widehat\beta_{j',k}^T Z\right) \right\}} \, .`
$$

# Generating Random Multistate Survival Data


# Acknowledgements

We acknowledge contributions from TBD.

# References