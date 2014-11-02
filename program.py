__author__ = 'loi'
lottery = '''
init:
    contract.storage[0] = msg.sender #store service's key
code:
    if msg.data[0] == 1:
        contract.storage[1] = msg.sender
        ours = (msg.value/100)*5
        contract.storage[2] = (msg.value - ours)
        contract.storage[3] = msg.data[1] #recipient
        send(1000, contract.storage[0], ours)
        return(0)
    elif (msg.data[0] == 2) and (contract.storage[3] == msg.sender) :
        send(1000, msg.sender, contract.storage[2])
        return(0)
    elif (msg.data[0] == 3) and (contract.storage[3] == msg.sender) :
        send(1000, contract.storage[1], contract.storage[2])
        return(0)

        
'''
import serpent
from pyethereum import transactions, blocks, processblock, utils
import time

code = serpent.compile(lottery)
key = utils.sha3('cow')
addr = utils.privtoaddr(key)
key2 = utils.sha3('cow2')
addr2 = utils.privtoaddr(key2)
key_host = utils.sha3('host')
add_host = utils.privtoaddr(key_host)


#initialize the block
genesis = blocks.genesis({addr: 10**18, addr2: 10**18, add_host: 10**18})

#This is to initialize the contract
tx1 = transactions.contract(0,10**12,10000,0,code).sign(key_host)
result, contract = processblock.apply_transaction(genesis, tx1)

#start buying tickets
#nonce, gasprice, startgas, to, value, data
price = 10**17
tx2 = transactions.Transaction(0, 10**12, 10000, contract, price,  serpent.encode_datalist([1,addr2])).sign(key)
result, ans = processblock.apply_transaction(genesis,tx2)
tx3 = transactions.Transaction(0, 10**12, 10000, contract,0,  serpent.encode_datalist([3])).sign(key2)
result, ans = processblock.apply_transaction(genesis,tx3)

print('Check address of service: %s ' %str(hex(genesis.get_storage_data(contract, 0))))
print('Sender address: %s' %str(hex(genesis.get_storage_data(contract, 1))))
print('Reciever address: %s' %str(hex(genesis.get_storage_data(contract, 3))))
print('Price: %s' %str(genesis.get_storage_data(contract, 2)))

#Mine serveral blocks
for i in range(5):
    genesis.finalize()
    t = (genesis.timestamp or int(time.time())) + 60
    genesis = blocks.Block.init_from_parent(genesis, add_host, '', t)



print 'balance of add %s is: %s' %(addr, str(genesis.get_balance(addr)))
print 'balance of add %s is: %s' %(addr2, str(genesis.get_balance(addr2)))
