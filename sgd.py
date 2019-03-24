#!/usr/bin/python3

import numpy as np
import time
## Based on code on basic SGD on linear regression: https://towardsdatascience.com/gradient-descent-in-python-a0d07285742f 

def  cal_cost(theta,X,y):
    '''
    
    Calculates the cost for given X and Y. The following shows and example of a single dimensional X
    theta = Vector of thetas 
    X     = Row of X's np.zeros((2,j))
    y     = Actual y's np.zeros((2,1))
    
    where:
        j is the no of features
    '''
    
    m = len(y)
    
    predictions = X.dot(theta)
    cost = (1/(2*m)) * np.sum(np.square(predictions-y))
    return cost

def compute_local_theta(m, X, y, theta, cost, machinespeed=0):
    rand_ind = np.random.randint(0,m)
    X_i = X[rand_ind,:].reshape(1, X.shape[1])
    y_i = y[rand_ind].reshape(1, 1
    )
    prediction = np.dot(X_i, theta)
    theta = theta -(1/m) * 0.5 * ( X_i.T.dot((prediction - y_i)))
    cost += cal_cost(theta,X_i,y_i)
    # SIMULATES MACHINE SPEED!!!
    time.sleep(machinespeed) 
    return theta, cost

def stochastic_gradient_descent(X,y,theta,iterations=1000):
    '''
    X    = Matrix of X with added bias units
    y    = Vector of Y
    theta=Vector of thetas np.random.randn(j,1)
    learning_rate 
    iterations = no of iterations
    
    Returns the final theta vector and array of cost history over no of iterations
    '''
    m = len(y)
    cost_history = np.zeros(iterations)
    for it in range(iterations):
        cost = 0.0
        for i in range(m):

            ## Compute update
            theta, cost = compute_local_theta(m, X, y, theta, cost)

        cost_history[it]  = cost
    return theta, cost_history

def main():
    X = 2 * np.random.rand(100,1)
    y = 4 + 3 * X + np.random.randn(100,1)
    n_iter = 50

    theta = np.random.randn(2,1)

    X_b = np.c_[np.ones((len(X),1)),X]
    theta,cost_history = stochastic_gradient_descent(X_b,y,theta,n_iter)

    print('Theta0:          {:0.3f},\nTheta1:          {:0.3f}'.format(theta[0][0],theta[1][0]))
    print('Final cost/MSE:  {:0.3f}'.format(cost_history[-1]))

if __name__ == "__main__":
    main()