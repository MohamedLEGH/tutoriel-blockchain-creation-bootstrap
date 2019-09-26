# query the chain


ip addr show

curl http://localhost:5000/chain


# make a transaction

#curl --header "Content-Type: application/json" --request POST --data '{"sender":"mohamed","receiver":"salim","amount":10}'  localhost:5000/transaction

#curl --header "Content-Type: application/json" --request POST --data '{"sender":"colas","receiver":"mohamed","amount":10}'  localhost:5000/transaction

#curl --header "Content-Type: application/json" --request POST --data '{"sender":"justine","receiver":"mohamed","amount":50}'  localhost:5000/transaction


# mine block

curl --request POST http://localhost:5000/mine_block