# Plantplusplus
<img width="597" height="193" alt="image" src="https://github.com/user-attachments/assets/4eada813-50ea-4ee2-984b-e81f36346b33" />

Plan++ is a personal project I created to simulate+model complex processing plants. Specifically the goal is to be able to quantitatively solve how seperators behave based on inputs using a monte carlo-like method.
The idea is to randomly chose recovery splits in a processing plant, measure error to the mass balance and refine the search. Additionally, the trials are allowed to branch to different generated systems with low error so as not to get "stuck" on the wrong system definition. For 3+ output separators that require 3 different recovery % numbers adding to one trials with the dirichlet distribution for rng have proved to be more difficult and currently use a more basic method but will upgrade later.

## Program Capabilities
1. Can solve for actual recovery numbers of separators given a system definition and mass balance
2. Can take multiple mass balances from the same system and run multiple regression models on the recovery curves based on the input feed to the system (however current # of types of regression is limited).

## How To Run
Run the plantplusplus.py file, this will take you to a CLI where you can choose to solve, analyse, or model your processing system.

## Recent Results:
Currently is able to find many relationships with R2 score >0.8 for basic test cases

## Project Next Steps:
1. Improve the regression algorithm. Note: Initial Symbolic Regression didnt prove to be super useful on the provided test cases, maybe real mine data would help
2. Make a remodelling feature available with the regression models defined
3. Add multiprocessing? Not sure that this makes sense because the only place this would be available is the simulation of the system which has very small runtime (MP overhead would take longer) and every other loop is very sequential.
4. Improve the ease of access for submitting systems and mass balances (clean up the excel sheets maybe make a gui?)
