# Plantplusplus
Plan++ is a personal project I created to simulate+model complex processing plants. Specifically the goal is to be able to quantitatively solve how seperators behave based on inputs using a monte carlo-like method.
The idea is to randomly chose recovery splits in a processing plant, measure error to the mass balance and refine the search. Additionally, the trials are allowed to branch to different generated systems with low error so as not to get "stuck" on the wrong system definition. For 3+ output separators that require 3 different recovery % numbers adding to one trials with the dirichlet distribution for rng have proved to be more difficult and currently use a more basic method but will upgrade later.

##Program Capabilities
1. Can solve for actual recovery numbers of separators given a system definition and mass balance
2. Can take multiple mass balances from the same system and run multiple regression models on the recovery curves based on the input feed to the system (however current # of types of regression is limited).

##How To Run
Run the main.py file, specifically right now there are 3 functions in the "main" loop that load the system, solve the recovery, and run regression on the solved recovery. Uncomment as needed, will add a better way later.

##Recent Results:
Currently is able to find many relationships with R2 score >0.8 for basic test cases

##Project Next Steps:
1. Improve the (non-existent) UI to a CLI that can load test cases, run the recovery solver and then run the regression solver. Also improve the output to something more readable/useful in an excel setting
2. Improve the regression algorithm. Note: Initial Symbolic Regression didnt prove to be super useful on the provided test cases, maybe real mine data would help
3. Add multiprocessing? Not sure that this makes sense because the only place this would be available is the simulation of the system which has very small runtime (MP overhead would take longer) and every other loop is very sequential.
4. Improve the ease of access for submitting systems and mass balances (clean up the excel sheets maybe make a gui?)
