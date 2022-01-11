# Solana Validator Manager


### Quick Install

* Log in to your server
* Create the key pair file (you can also upload it via scp if you prefer):
  ````shell
  nano ~/validator-keypair.json
  ````   
  Paste your key pair, save the file (ctrl-O) and exit (ctrl-X).


  If you have a *vote account* key pair, create the key pair file (or upload it via scp):
  ````shell
   nano ~/vote-account-keypair.json
  ````  
  Paste your key pair, save the file (ctrl-O) and exit (ctrl-X).
* Run this command…

````shell
/bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/NEWSOROS/sv-manager/main/install/install_validator.sh)"
````
### How to setup old node
````shell
curl -fsSL https://raw.githubusercontent.com/NEWSOROS/sv-manager/main/install/install_monitoring_old_server.sh | /bin/bash -s -- v019-testnet
````
### How to update validator

````shell
/bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/NEWSOROS/sv-manager/main/install/update_test_validator_version.sh)" --version 1.8.11
````

### how to update monitoring

````shell
/bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/NEWSOROS/sv-manager/main/install/update_monitoring.sh)" 
````


### If you want more control over the configuration of your node, please refer to the [advanced technical specifications](docs/advanced.md)


## Useful links

* [Solana](https://solana.com/)
* [Validator docs](https://docs.solana.com/running-validator)
