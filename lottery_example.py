__author__ = 'loi'
lottery = '''
init:
    #Record the initiator
    contract.storage[0] = msg.sender
    contract.storage[1] = 0 #no. of sold tickets
    contract.storage[2] = block.timestamp
code:
    # If a message with 9 item is sent, that's a buy request
    MAXIMUM_TICKETS = 2
    if msg.datasize == 0:
        if msg.value < 10**15:
            return(1)
        if contract.storage[1] == MAXIMUM_TICKETS:
            return(1)

        buyer = msg.sender
        contract.storage[1] = contract.storage[1] + 1
        contract.storage[3+contract.storage[1]] = buyer
        #mark when all the tickets are sold
        if contract.storage[1] == MAXIMUM_TICKETS:
            contract.storage[2] = block.timestamp
        return (0)

    # If a message with one item [check] is sent, that's a draw request
    elif msg.datasize == 1:
        #check if all the tickets are sold
        if contract.storage[1] < MAXIMUM_TICKETS:
            return(2)
        if block.timestamp - contract.storage[2] < 100:
            return(2)
        #start drawing
        t = block.prevhash%MAXIMUM_TICKETS
        send(1000, contract.storage[3+t+1], MAXIMUM_TICKETS*(10**15))
        return (3+t+1)
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
tx2 = transactions.Transaction(0, 10**12, 10000, contract, 10**15,  serpent.encode_datalist([])).sign(key)
result, ans = processblock.apply_transaction(genesis,tx2)

tx3 = transactions.Transaction(0, 10**12, 10000, contract, 10**15,  serpent.encode_datalist([])).sign(key2)
result, ans = processblock.apply_transaction(genesis,tx3)

print('Check no. of buyers: %s ' %str(genesis.get_storage_data(contract, 1)))
print('Check address of ticket 1: %s ' %str(hex(genesis.get_storage_data(contract, 4))))
print 'balance ' + str(genesis.get_balance(addr))
print('Check address of ticket 2: %s ' %str(hex(genesis.get_storage_data(contract, 5))))
print 'balance ' + str(genesis.get_balance(addr2))

#Mine serveral blocks
for i in range(5):
    genesis.finalize()
    t = (genesis.timestamp or int(time.time())) + 60
    genesis = blocks.Block.init_from_parent(genesis, add_host, '', t)

#anyone can send the transaction to request the draw if it is in proper time.
#we let the host send it to make the transaction clearer
tx4 = transactions.Transaction(1, 10**12, 10000, contract, 0,  serpent.encode_datalist([1])).sign(key_host)
result, ans = processblock.apply_transaction(genesis,tx4)
print('Winner of the draw is: %s' %str(hex(genesis.get_storage_data(contract, ans))))

print 'balance of add %s is: %s' %(addr, str(genesis.get_balance(addr)))
print 'balance of add %s is: %s' %(addr2, str(genesis.get_balance(addr2)))