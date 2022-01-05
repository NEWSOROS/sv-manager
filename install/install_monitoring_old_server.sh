#!/bin/bash
#set -x -e


install_monitoring () {

  inventory="testnet.yaml" # mainnet.yaml testnet.yaml


  VALIDATOR_NAME=$1
  PATH_TO_VALIDATOR_KEYS=/home/sol
  SOLANA_USER="sol"
  
  if [ ! -f "$PATH_TO_VALIDATOR_KEYS/validator-keypair.json" ]
  then
    echo "key $PATH_TO_VALIDATOR_KEYS/validator-keypair.json not found. Pleas verify and run the script again"
    exit
  fi
  if [ ! -f "$PATH_TO_VALIDATOR_KEYS/vote-account-keypair.json" ]
  then
    echo "key $PATH_TO_VALIDATOR_KEYS/vote-account-keypair.json not found. Pleas verify and run the script again"
    exit
  fi
  
  cd
  rm -rf sv_manager/

  if [[ $(which apt | wc -l) -gt 0 ]]
  then
  pkg_manager=apt
  elif [[ $(which yum | wc -l) -gt 0 ]]
  then
  pkg_manager=yum
  fi

  echo "### Update packages... ###"
  $pkg_manager update
  echo "### Install ansible, curl, unzip... ###"
  $pkg_manager install ansible curl unzip --yes

  ansible-galaxy collection install ansible.posix
  ansible-galaxy collection install community.general

  echo "### Download Solana validator manager"
  cmd="https://github.com/NEWSOROS/sv-manager/archive/refs/tags/$2.zip"
  echo "starting $cmd"
  curl -fsSL "$cmd" --output sv_manager.zip
  echo "### Unpack Solana validator manager ###"
  unzip ./sv_manager.zip -d .

  mv sv-manager* sv_manager
  rm ./sv_manager.zip
  cd ./sv_manager || exit
  cp -r ./inventory_example ./inventory

  #echo $(pwd)
  ansible-playbook --connection=local --inventory ./inventory/$inventory --limit local  playbooks/pb_config.yaml -vvv --extra-vars "{ \
  'solana_user': '$SOLANA_USER', \
  'validator_name':'$VALIDATOR_NAME', \
  'local_secrets_path': '$PATH_TO_VALIDATOR_KEYS' \
  }"

  ansible-playbook --connection=local --inventory ./inventory/$inventory --limit local  playbooks/pb_install_monitoring.yaml --extra-vars "@/etc/sv_manager/sv_manager.conf"

  echo "### Cleanup install folder ###"
  cd ..
  rm -r ./sv_manager
  echo "### Cleanup install folder done ###"
  echo "### Check your dashboard: https://solana.thevalidators.io/d/e-8yEOXMwerfwe/solana-monitoring?&var-server="$VALIDATOR_NAME

  $pkg_manager remove ansible --yes

}

install_monitoring "${1}" "${2:-latest}"
