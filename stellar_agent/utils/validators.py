"""Input validation utilities."""
import re

def is_valid_stellar_address(address: str) -> bool:
    """
    Validate Stellar public key format.
    
    Args:
        address: Public key to validate
        
    Returns:
        True if valid, False otherwise
    """
    if not address:
        return False
    
    # Stellar public keys start with 'G' and are 56 characters long
    pattern = r'^G[A-Z2-7]{55}$'
    return bool(re.match(pattern, address))

def is_valid_amount(amount: float) -> bool:
    """
    Validate payment amount.
    
    Args:
        amount: Amount to validate
        
    Returns:
        True if valid, False otherwise
    """
    return amount > 0

def validate_amount_range(amount: float, max_xlm: float = 10000) -> bool:
    """Validate amount is within safe range."""
    return 0 < amount <= max_xlm