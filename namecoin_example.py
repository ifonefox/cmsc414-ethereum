namecoin_code = """                                                                                                                                                                                                               
// Namecoin                                                                                                                                                                                                                       
                                                                                                                                                                                                                                  
if !contract.storage[msg.data[0]]: # Is the key not yet taken?                                                                                                                                                                    
    # Then take it!                                                                                                                                                                                                               
    contract.storage[msg.data[0]] = msg.data[1]                                                                                                                                                                                   
    return(1)                                                                                                                                                                                                                     
else:                                                                                                                                                                                                                             
    return(0) // Otherwise do nothing                                                                                                                                                                                             
"""

import serpent
from pyethereum import transactions, blocks, processblock, utils
processblock.print_debug = 1
code = serpent.compile(namecoin_code)
key = utils.sha3('cow')
addr = utils.privtoaddr(key)
genesis = blocks.genesis({ addr: 10**18 })
tx1 = transactions.contract(0,10**12,10000,0,code).sign(key)
result, contract = processblock.apply_transaction(genesis,tx1)
print genesis.to_dict()
tx2 = transactions.Transaction(1,10**12,10000,contract,0,
     serpent.encode_datalist(['george',45])).sign(key)
result, ans = processblock.apply_transaction(genesis,tx2)
serpent.decode_datalist(ans)
print genesis.to_dict()