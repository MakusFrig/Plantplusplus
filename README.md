# Plantplusplus
<img width="597" height="193" alt="image" src="https://github.com/user-attachments/assets/4eada813-50ea-4ee2-984b-e81f36346b33" />

Plan++ is a personal project I created to simulate+model complex processing plants with excel inputs in mind. Specifically the goal is to be able to quantitatively solve how seperators behave based on inputs using a monte carlo-like method. The idea is to randomly chose recovery splits in a processing plant, measure error to the mass balance and refine the search. Additionally, the trials are allowed to branch to different generated systems with low error so as not to get "stuck" on the wrong system definition. For 3+ output separators that require 3 different recovery % numbers adding to one trials with the dirichlet distribution for rng have proved to be more difficult and currently use a more basic method but will upgrade later.

## Program Capabilities
1. Can solve for actual recovery numbers of separators given a system definition and mass balance.
<img width="1044" height="713" alt="image" src="https://github.com/user-attachments/assets/9b84e684-7a56-4988-9ce9-68826d1fc3b5" />
2. Can analyse the solved system using basic symbolic regression, allowing the user to choose the no. of features used for regression to improve accuracy.
<img width="966" height="492" alt="image" src="https://github.com/user-attachments/assets/659a6805-39f3-4022-b302-b1c6bd00c735" />
3. Users can save/load the models from the analysis to interpret new mass balance numbers, modelling future plant outputs.
<img width="965" height="288" alt="image" src="https://github.com/user-attachments/assets/2b067f41-2692-4167-8b42-05f07b620cba" />

## Recent Results:
Now fully able to Solve, Analyse, and Model processing plants

## How To Run
Run the plantplusplus.py file, this will take you to a CLI where you can choose to solve, analyse, or model your processing system.
There are currently test cases to try

###Inputs
Currently uses basic excel sheets to define a system of sources, separators, and collectors.
<img width="298" height="200" alt="image" src="https://github.com/user-attachments/assets/9763265e-60fd-470a-9f8b-262cf198adc6" />
As shown above first column is type definition, second is name, third+ are the outputs if a separator. More docs to come.

## Project Next Steps:
1. Improve the regression algorithm. Note: Initial Symbolic Regression didnt prove to be super useful on the provided test cases, maybe real mine data would help
2. Make a remodelling feature available with the regression models defined
3. Add multiprocessing? Not sure that this makes sense because the only place this would be available is the simulation of the system which has very small runtime (MP overhead would take longer) and every other loop is very sequential.
4. Improve the ease of access for submitting systems and mass balances (clean up the excel sheets maybe make a gui?)
