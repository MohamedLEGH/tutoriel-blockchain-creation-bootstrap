import time
from transaction import Transaction
from block import Block

difficulty = 4

first_block = Block(0,"")

tx = Transaction("mohamed","justine",50, time.time())

first_block.add_transaction(tx)
first_block.mine(difficulty)

print("First block is: ")

print(first_block)

last_hash = first_block.hashval

second_block = Block(1,last_hash)

second_block.mine(difficulty)

print("Second block is: ")

print(second_block)