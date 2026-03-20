"""Unit tests for StellarClient."""
import pytest
from decimal import Decimal
from unittest.mock import Mock, patch
from stellar_agent.client import StellarClient


@pytest.fixture
def mock_config():
    with patch('stellar_agent.client.config') as mock_conf:
        mock_conf.horizon_url = 'https://horizon-testnet.stellar.org'
        mock_conf.network_passphrase = 'Test SDF Network ; September 2015'
        mock_conf.balance_check_enabled = True
        mock_conf.minimum_balance_xlm = 1.0
        yield mock_conf


def test_stellar_client_init(mock_config):
    """Test StellarClient initialization."""
    with patch('stellar_agent.client.Server') as mock_server:
        client = StellarClient()
        mock_server.assert_called_once_with('https://horizon-testnet.stellar.org')
        assert client.server == mock_server.return_value


def test_get_account_info(mock_config):
    """Test fetching account information."""
    with patch('stellar_agent.client.Server') as mock_server_class:
        expected = {
            'id': 'GBRPYHIL2CI3FNQ4BXLFMNDLFJUNPU2HY3ZMFSHONUCEOASW7QC7OX2H',
            'sequence': '123456',
            'balances': [{'asset_type': 'native', 'balance': '100.00'}],
        }
        mock_server_class.return_value \
            .accounts.return_value \
            .account_id.return_value \
            .call.return_value = expected

        client = StellarClient()
        result = client.get_account_info('GBRPYHIL2CI3FNQ4BXLFMNDLFJUNPU2HY3ZMFSHONUCEOASW7QC7OX2H')
        assert result == expected


def test_get_account_info_not_found(mock_config):
    """get_account_info raises RuntimeError when account does not exist."""
    from stellar_sdk.exceptions import NotFoundError
    with patch('stellar_agent.client.Server') as mock_server_class:
        mock_response = Mock()
        mock_response.status_code = 404
        mock_response.text = 'Not found'
        mock_server_class.return_value \
            .accounts.return_value \
            .account_id.return_value \
            .call.side_effect = NotFoundError(mock_response)

        client = StellarClient()
        with pytest.raises(RuntimeError, match='not found on the Stellar network'):
            client.get_account_info('GBRPYHIL2CI3FNQ4BXLFMNDLFJUNPU2HY3ZMFSHONUCEOASW7QC7OX2H')


def test_send_payment_success(mock_config):
    """send_payment builds, signs, and submits a transaction."""
    with patch('stellar_agent.client.Server') as mock_server_class, \
         patch('stellar_agent.client.Keypair') as mock_keypair_class, \
         patch('stellar_agent.client.TransactionBuilder') as mock_tx_class, \
         patch('stellar_agent.client.Payment'):

        mock_server = mock_server_class.return_value
        mock_keypair = Mock()
        mock_keypair.public_key = 'GBRPYHIL2CI3FNQ4BXLFMNDLFJUNPU2HY3ZMFSHONUCEOASW7QC7OX2H'
        mock_keypair_class.from_secret.return_value = mock_keypair

        mock_server.accounts.return_value \
            .account_id.return_value \
            .call.return_value = {
                'balances': [{'asset_type': 'native', 'balance': '200.0000000'}]
            }
        mock_server.load_account.return_value = Mock()

        mock_tx = mock_tx_class.return_value
        mock_tx.append_operation.return_value = mock_tx
        mock_tx.set_timeout.return_value = mock_tx
        mock_transaction = Mock()
        mock_tx.build.return_value = mock_transaction

        expected = {'hash': 'abc123', 'ledger': 1234}
        mock_server.submit_transaction.return_value = expected

        client = StellarClient()
        result = client.send_payment(
            source_secret='SBRPYHIL2CI3FNQ4BXLFMNDLFJUNPU2HY3ZMFSHONUCEOASW7QC7OX2H',
            destination_public='GBRPYHIL2CI3FNQ4BXLFMNDLFJUNPU2HY3ZMFSHONUCEOASW7QC7OX2H',
            amount=10.5,
        )
        mock_transaction.sign.assert_called_once_with(mock_keypair)
        mock_server.submit_transaction.assert_called_once_with(mock_transaction)
        assert result == expected


def test_send_payment_insufficient_balance(mock_config):
    """send_payment raises RuntimeError when balance is too low."""
    with patch('stellar_agent.client.Server') as mock_server_class, \
         patch('stellar_agent.client.Keypair') as mock_keypair_class:

        mock_keypair = Mock()
        mock_keypair.public_key = 'GBRPYHIL2CI3FNQ4BXLFMNDLFJUNPU2HY3ZMFSHONUCEOASW7QC7OX2H'
        mock_keypair_class.from_secret.return_value = mock_keypair
        mock_server_class.return_value \
            .accounts.return_value \
            .account_id.return_value \
            .call.return_value = {
                'balances': [{'asset_type': 'native', 'balance': '0.5000000'}]
            }

        client = StellarClient()
        with pytest.raises(RuntimeError, match='Balance check failed'):
            client.send_payment(
                source_secret='SBRPYHIL2CI3FNQ4BXLFMNDLFJUNPU2HY3ZMFSHONUCEOASW7QC7OX2H',
                destination_public='GBRPYHIL2CI3FNQ4BXLFMNDLFJUNPU2HY3ZMFSHONUCEOASW7QC7OX2H',
                amount=100.0,
            )


def test_send_payment_balance_check_disabled(mock_config):
    """Payment proceeds without balance check when disabled."""
    mock_config.balance_check_enabled = False
    with patch('stellar_agent.client.Server') as mock_server_class, \
         patch('stellar_agent.client.Keypair') as mock_keypair_class, \
         patch('stellar_agent.client.TransactionBuilder') as mock_tx_class, \
         patch('stellar_agent.client.Payment'):

        mock_keypair = Mock()
        mock_keypair.public_key = 'GBRPYHIL2CI3FNQ4BXLFMNDLFJUNPU2HY3ZMFSHONUCEOASW7QC7OX2H'
        mock_keypair_class.from_secret.return_value = mock_keypair
        mock_server = mock_server_class.return_value
        mock_server.load_account.return_value = Mock()
        mock_tx = mock_tx_class.return_value
        mock_tx.append_operation.return_value = mock_tx
        mock_tx.set_timeout.return_value = mock_tx
        mock_tx.build.return_value = Mock()
        mock_server.submit_transaction.return_value = {'hash': 'xyz789'}

        client = StellarClient()
        result = client.send_payment(
            source_secret='SBRPYHIL2CI3FNQ4BXLFMNDLFJUNPU2HY3ZMFSHONUCEOASW7QC7OX2H',
            destination_public='GBRPYHIL2CI3FNQ4BXLFMNDLFJUNPU2HY3ZMFSHONUCEOASW7QC7OX2H',
            amount=10.5,
        )
        assert result == {'hash': 'xyz789'}
        mock_server.accounts.assert_not_called()
