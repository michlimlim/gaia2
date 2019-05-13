## Architecture diagram I drew is here:
Slide 26 of [Shiqiang presentation](https://docs.google.com/presentation/d/1Dtv1gzUL4RYNRVZy3klMeuQvE4mSCzqIr4H5uZWfZK8/edit#slide=id.p)

## Evaluation results and charts are here:
[Evaluation Results!](https://docs.google.com/spreadsheets/d/1ji5fK3A6w5Z5J2BaNI0rOgBkhw1p8eWiYvdOftzuJw4/edit#gid=787187439)
Each tab is labelled. I performed around 10 experiments for each setting. 

## Terminal commands

I ran all the tests using 2 nodes. Run these on separate terminals:
```
python main.py -me localhost:5000 -leader localhost:5000 -them localhost:5001 
```
```
python main.py -me localhost:5001 -leader localhost:5000 -them localhost:5000
```

## Tuning parameters and settings
For most of the tests, the for loop in `main.py` will run the experiments on loop and so we just read the output for the results of all 10 tests. 

The for loop and surrounding code are designed to stop each node until the other node is done with their experiment and reached convergence. However, at this current state, we do not support more than 2 nodes. Take a look at whereever we write the MLThread.close to see how we coordinate between the ends of two nodes. That will help you see how to code this to deal with more than 2 nodes. 

### Bias
We have the iid way of partitioning and the non-iid way. The default is the non-iid since that is what federated learning data is like. To set as iid partitioning, find this line in `main.py` and change the last argument to False. 
```
node = initialize_current_node(pending_work_queues, 'MNIST', './data', False)
```

### How to set one device to be slower
Go to `ml_thread.py`. Uncomment this line:
```
if self.ip_addr == 'localhost:5000':
    time.sleep(1)
```
This makes the 'localhost:5000' or other hardcoded addresses of your choice SLEEP for 1 second before sending out an update.

### How to set model for synchronicity or asynchronicity
Go to `ml_thread.py`. Uncomment the top code and comment out bottom code for synchronicity. Uncomment the bottom code and comment out top code for asynchronicity.

```
while self.pending_work_queues.total_no_of_updates < len(self.pending_work_queues.other_hosts):
        time.sleep(0.0001)
self.aggregate_received_updates()
```
```
while self.pending_work_queues.total_no_of_updates > 0:
    self.aggregate_received_updates()
```
### Switching between naive averaging and our BiasControl alg
Go to `device_fairness.py` and find the `get_alphas` function declaration.
Use this line for naive averaging
```
return [1.00/len(v)] * len(v)
```
and this for our get_weights:
```
return get_weights(v)
```