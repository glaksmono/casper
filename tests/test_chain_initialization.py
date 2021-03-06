import pytest

from ethereum import utils
from ethereum.tools.tester import TransactionFailed
from conftest import casper_chain


def test_rlp_decoding_is_pure(
        casper_chain,
        base_sender_privkey,
        vyper_rlp_decoder_address,
        purity_checker_address,
        purity_checker_ct
        ):
    purity_return_val = casper_chain.tx(
        base_sender_privkey,
        purity_checker_address,
        0,
        purity_checker_ct.encode('submit', [vyper_rlp_decoder_address])
    )
    assert utils.big_endian_to_int(purity_return_val) == 1


def test_msg_hasher_is_pure(
        casper_chain,
        base_sender_privkey,
        msg_hasher_address,
        purity_checker_address,
        purity_checker_ct
        ):
    purity_return_val = casper_chain.tx(
        base_sender_privkey,
        purity_checker_address,
        0,
        purity_checker_ct.encode('submit', [msg_hasher_address])
    )
    assert utils.big_endian_to_int(purity_return_val) == 1


# sanity check on casper contract basic functionality
def test_init_first_epoch(casper, new_epoch):
    assert casper.current_epoch() == 0
    assert casper.next_validator_index() == 1

    new_epoch()

    assert casper.dynasty() == 0
    assert casper.next_validator_index() == 1
    assert casper.current_epoch() == 1
    assert casper.total_slashed(casper.current_epoch()) == 0


@pytest.mark.parametrize(
    'start_epoch',
    [
        (0), (1), (4), (10)
    ]
)
def test_start_epoch(test_chain, start_epoch, epoch_length, casper_args, deploy_casper_contract):
    test_chain.mine(
        epoch_length * start_epoch - test_chain.head_state.block_number
    )

    casper = deploy_casper_contract(casper_args)
    assert casper.START_EPOCH() == start_epoch
    assert casper.current_epoch() == start_epoch


@pytest.mark.parametrize(
    'epoch_length, success',
    [
        (-1, False),
        (0, False),
        (10, True),
        (250, True),
        (256, False),
        (500, False),
    ]
)
def test_epoch_length(epoch_length, success, casper_args,
                      deploy_casper_contract, assert_failed):
    # Note: cannot use assert_tx_failed because requires casper_chain
    if not success:
        assert_failed(
            lambda: deploy_casper_contract(casper_args),
            TransactionFailed
        )
        return

    casper = deploy_casper_contract(casper_args)
    assert casper.EPOCH_LENGTH() == epoch_length
