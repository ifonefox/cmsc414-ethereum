__author__ = 'adam-jordan-max-sean'
escrow = '''
init:
    contract.storage[0] = msg.sender #store service's key
code:
    if msg.data[0] == 1:
        contract.storage[1] = msg.sender
        ours = (msg.value/100)*5
        contract.storage[2] = (msg.value - ours)
        contract.storage[3] = msg.data[1] #recipient
        contract.storage[4] = 0 #sender confirm
        contract.storage[5] = 0 #recepient confirm
        send(1000, contract.storage[0], ours)
        return(0)
    elif (msg.data[0] == 2) and (contract.storage[3] == msg.sender) :
        contract.storage[5] = 1
        if (contract.storage[4] == 1): #both confirmed, send
            send(1000, contract.storage[3], contract.storage[2])
        elif (contract.storage[4] == -1): #disagreement. Contract should contact authorities, or wait for an agreement
            return(0)
        return(0)
    elif (msg.data[0] == 3) and (contract.storage[3] == msg.sender) :
        contract.storage[5] = -1
        if (contract.storage[4] == -1): #both denied, return  
            send(1000, contract.storage[1], contract.storage[2])
        elif (contract.storage[4] == 1): #disagreement. Contract should contact authorities, or wait for an agreement
            return(0)
        return(0)
    elif (msg.data[0] == 2) and (contract.storage[1] == msg.sender) :
        contract.storage[4] = 1
        if (contract.storage[5] == 1): #both confirmed, send
            send(1000, contract.storage[3], contract.storage[2])
        elif (contract.storage[5] == -1): #disagreement. Contract should contact authorities, or wait for an agreement
            return(0)
        return(0)
    elif (msg.data[0] == 3) and (contract.storage[1] == msg.sender) :
        contract.storage[4] = -1
        if (contract.storage[5] == -1): #both denied, return  
            send(1000, contract.storage[1], contract.storage[2])
        elif (contract.storage[5] == 1): #disagreement. Contract should contact authorities, or wait for an agreement
            return(0)
        return(0)


        
'''
import serpent
from pyethereum import transactions, blocks, processblock, utils
import time
import sys

#require command line args
if len(sys.argv) < 3:
    print("Usage: %s [price] [recipient: transcation success: 2, transcation deny: 3]  [sender: transcation success: 2, transcation deny: 3]" %sys.argv[0])
    sys.exit(1)

code = serpent.compile(escrow)
sender_key = utils.sha3('sender')
sender_addr = utils.privtoaddr(sender_key)
recipient_key = utils.sha3('recipient')
recipient_addr = utils.privtoaddr(recipient_key)
host_key = utils.sha3('host')
host_addr = utils.privtoaddr(host_key)

#initialize the block
genesis = blocks.genesis({sender_addr: 10**18, recipient_addr: 10**18, host_addr: 10**18})

#initialize the contract
tx1 = transactions.contract(0, 10**12, 10000, 0, code).sign(host_key)
result, contract = processblock.apply_transaction(genesis, tx1)

#execute escrow transaction
#nonce, gasprice, startgas, to, value, data
price = int(sys.argv[1]) #user supplied price
tx2 = transactions.Transaction(0, 10**12, 10000, contract, price, serpent.encode_datalist([1,recipient_addr])).sign(sender_key)
result, ans = processblock.apply_transaction(genesis, tx2)
tx3 = transactions.Transaction(0, 10**12, 10000, contract, 0, serpent.encode_datalist([int(sys.argv[2])])).sign(recipient_key)
result, ans = processblock.apply_transaction(genesis, tx3)
tx4 = transactions.Transaction(1, 10**12, 10000, contract, 0, serpent.encode_datalist([int(sys.argv[3])])).sign(sender_key)
result, ans = processblock.apply_transaction(genesis, tx4)

print('Service address:  %s ' %str(hex(genesis.get_storage_data(contract, 0))))
print('Sender address:   %s' %str(hex(genesis.get_storage_data(contract, 1))))
print('Reciever address: %s\n' %str(hex(genesis.get_storage_data(contract, 3))))
print('Price: %s' %str(genesis.get_storage_data(contract, 2)))

#mine serveral blocks
for i in range(5):
    genesis.finalize()
    t = (genesis.timestamp or int(time.time())) + 60
    genesis = blocks.Block.init_from_parent(genesis, host_addr, '', t)

print 'Sender balance    (%s): %s' %(sender_addr, str(genesis.get_balance(sender_addr)))
print 'Recipient balance (%s): %s' %(recipient_addr, str(genesis.get_balance(recipient_addr)))
