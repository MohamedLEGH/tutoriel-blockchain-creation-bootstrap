from chain import Blockchain

difficulty = 4

blockchain =  Blockchain(difficulty)
blockchain.create_genesis_block()

print("blockchain: ")
print(blockchain.to_dict())

first_block = blockchain.chain[-1]

print("First block: ")
print(first_block)

blockchain.add_transaction("mohamed","colas", 10)
blockchain.add_transaction("mohamed","salim", 30)
blockchain.add_transaction("salim","colas", 10)
blockchain.mine_block()

print("blockchain: ")
print(blockchain.to_dict())
second_block = blockchain.chain[-1]

print("Second block: ")
print(second_block)

