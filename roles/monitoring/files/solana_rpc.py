from common import ValidatorConfig
from typing import Optional
from common import debug
from request_utils import execute_cmd_str, smart_rpc_call, rpc_call
import subprocess
import json
import time
from datetime import datetime, timedelta


def load_identity_account_pubkey(config: ValidatorConfig) -> Optional[str]:
    """
    loads validator identity account pubkey
    :param config: Validator Configuration
    :return: returns validator identity pubkey or None
    """
    identity_cmd = f'solana address -u localhost --keypair ' + config.secrets_path + '/validator-keypair.json'
    debug(config, identity_cmd)
    return execute_cmd_str(config, identity_cmd, convert_to_json=False)


def load_vote_account_pubkey(config: ValidatorConfig) -> Optional[str]:
    """
    loads vote account pubkey
    :param config: Validator Configuration
    :return: returns vote account pubkey  or None
    """
    vote_pubkey_cmd = f'solana address -u localhost --keypair ' + config.secrets_path + '/vote-account-keypair.json'
    debug(config, vote_pubkey_cmd)
    return execute_cmd_str(config, vote_pubkey_cmd, convert_to_json=False)


def load_vote_account_balance(config: ValidatorConfig, vote_account_pubkey: str):
    """
    loads vote account balance
    https://docs.solana.com/developing/clients/jsonrpc-api#getbalance
    """
    return smart_rpc_call(config, "getBalance", [vote_account_pubkey], {})


def load_identity_account_balance(config: ValidatorConfig, identity_account_pubkey: str):
    """
    loads identity account balance
    https://docs.solana.com/developing/clients/jsonrpc-api#getbalance
    """
    return smart_rpc_call(config, "getBalance", [identity_account_pubkey], {})


def load_epoch_info(config: ValidatorConfig):
    """
    loads epoch info
    https://docs.solana.com/developing/clients/jsonrpc-api#getepochinfo
    """
    return smart_rpc_call(config, "getEpochInfo", [], {})


def load_leader_schedule(config: ValidatorConfig, identity_account_pubkey: str):
    """
    loads leader schedule
    https://docs.solana.com/developing/clients/jsonrpc-api#getleaderschedule
    """
    params = [
        None,
        {
            'identity': identity_account_pubkey
        }
    ]
    return smart_rpc_call(config, "getLeaderSchedule", params, {})


def load_block_production(config: ValidatorConfig, identity_account_pubkey: str):
    """
    loads block production
    https://docs.solana.com/developing/clients/jsonrpc-api#getblockproduction
    """
    params = [
        {
            'identity': identity_account_pubkey
        }
    ]
    return smart_rpc_call(config, "getBlockProduction", params, {})


def load_block_production_cli(config: ValidatorConfig):
    cmd = f'solana block-production -u l --output json-compact'
    return execute_cmd_str(config, cmd, convert_to_json=True, default={})


def load_vote_accounts(config: ValidatorConfig, vote_account_pubkey: str):
    """
    loads block production
    https://docs.solana.com/developing/clients/jsonrpc-api#getvoteaccounts
    """
    params = [
        {
            'votePubkey': vote_account_pubkey
        }
    ]
    return smart_rpc_call(config, "getVoteAccounts", params, {})


def load_recent_performance_sample(config: ValidatorConfig):
    """
    loads recent performance sample
    https://docs.solana.com/developing/clients/jsonrpc-api#getrecentperformancesamples
    """
    params = [1]
    return rpc_call(config, config.remote_rpc_address, "getRecentPerformanceSamples", params, [], [])


def load_solana_version(config: ValidatorConfig):
    """
    loads solana version
    https://docs.solana.com/developing/clients/jsonrpc-api#getversion
    """
    return rpc_call(config, config.local_rpc_address, "getVersion", [], [], [])


def load_stake_account_rewards(config: ValidatorConfig, stake_account):
    cmd = f'solana stake-account ' + stake_account + ' --num-rewards-epochs=1 --with-rewards --output json-compact'
    return execute_cmd_str(config, cmd, convert_to_json=True)


def load_solana_validators(config: ValidatorConfig):
    cmd = f'solana validators -ul --output json-compact'
    data = execute_cmd_str(config, cmd, convert_to_json=True)
    
    if data is not None and 'validators' in data:
        validators = data['validators']
        sorted_validators = sorted(validators, key=lambda x: x.get('epochCredits', 0), reverse=True)
        for i, validator in enumerate(sorted_validators, start=1):
            validator['place'] = i
        return sorted_validators
    return None


def load_stakes(config: ValidatorConfig, vote_account):
    cmd = f'solana stakes ' + vote_account + ' --output json-compact'
    return execute_cmd_str(config, cmd, convert_to_json=True, default=[])


def load_block_time(config: ValidatorConfig, block):
    """
    loads solana version
    https://docs.solana.com/developing/clients/jsonrpc-api#getblocktime
    """
    params = [block]
    return rpc_call(config, config.local_rpc_address, "getBlockTime", params, None, None)

#    cmd = f'solana block-time -u l ' + str(block) + ' --output json-compact'
#    return execute_cmd_str(cmd, convert_to_json=True)


def try_to_load_current_block_info(config: ValidatorConfig):
    epoch_info_data = load_epoch_info(config)

    if epoch_info_data is not None:
        slot_index = epoch_info_data['slotIndex']
        absolute_slot = epoch_info_data['absoluteSlot']

        block_time_data = load_block_time(config, absolute_slot)

        if block_time_data is not None:
            return {
                'slot_index':  slot_index,
                'absolute_block': absolute_slot,
                'block_time': block_time_data['timestamp']
            }

    return None


def load_current_block_info(config: ValidatorConfig):
    result = None
    max_tries = 10
    current_try = 0
    while result is None and current_try < max_tries:
        result = try_to_load_current_block_info(config)
        current_try = current_try + 1

    return result


def load_cpu_model(config: ValidatorConfig):
    cmd = 'cat /proc/cpuinfo  | grep name| uniq'
    cpu_info = execute_cmd_str(config, cmd, False).split(":")
    cpu_model = cpu_info[1].strip()

    if cpu_model is not None:
        return cpu_model
    else:
        return 'Unknown'


def load_solana_validators_full(config: ValidatorConfig):
    cmd = f'solana validators -ul --output json-compact'
    return execute_cmd_str(config, cmd, convert_to_json=True)


def load_solana_validators_info(config: ValidatorConfig):
    cmd = f'solana validator-info get --url ' + config.remote_rpc_address + ' --output json-compact'
    data = execute_cmd_str(config, cmd, convert_to_json=True)
    return data


def load_solana_gossip(config: ValidatorConfig):
    cmd = f'solana gossip -ul --output json-compact'
    return execute_cmd_str(config, cmd, convert_to_json=True)

# Function to get current time
def get_current_time():
    return datetime.now()

def load_relayer_current_connectivity(config: ValidatorConfig):
    log_command = f"sudo journalctl --since '5 hours ago' -u relayer -o cat | grep 'Current epoch connectivity' | tail -n 1"
    result = subprocess.run(log_command, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    
    # Check if there's an error in stderr
    if result.stderr:
        error_message = result.stderr.decode('utf-8').strip()
        if "Failed to iterate through journal: Bad message" in error_message:
            #print("Journal error: Bad message. Check journal system health.")
            return {'log_delay': None, 'connectivity': None, 'error': 0}  # Return True to indicate an error
        else:
            #print(f"Other journal error: {error_message}")
            return {'log_delay': None, 'connectivity': None, 'error': 0}  # Return True to indicate an error
    
    log_line = result.stdout.decode('utf-8').strip()
    
    if log_line:
        try:
            # Extract timestamp and percentage
            log_time_str = log_line.split('[')[1].split(']')[0].split(' ')[0]  # Parse only the time part
            log_time = datetime.strptime(log_time_str, '%Y-%m-%dT%H:%M:%S.%fZ')
            current_time = get_current_time()
            log_delay = int((current_time - log_time).total_seconds())
            connectivity = float(log_line.split("Current epoch connectivity: ")[1].replace('%', ''))
            #print(f"Log entry found: {log_time}, connectivity: {connectivity}%")
            return {'log_delay': log_delay, 'connectivity': connectivity, 'error': 1}  # Return False to indicate no error
            #return {'connectivity': connectivity, 'error': False}  # Return False to indicate no error
        except Exception as e:
            #print(f"Error parsing log line: {e}")
            return {'log_delay': None, 'connectivity': None, 'error': 0}  # Return True to indicate an error
    else:
        #print("No log entries found")
        return {'log_delay': None, 'connectivity': None, 'error': 1}  # Return False, as no error but no log found either
 
