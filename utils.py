import os

def load_alpaca_credentials(filepath):
    """
    Parses the Alpaca credentials from the given text file.
    Handles both half-width (:) and full-width (：) colons.
    """
    credentials = {}
    if not os.path.exists(filepath):
        raise FileNotFoundError(f"Credential file not found at {filepath}")
    
    with open(filepath, 'r', encoding='utf-8') as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            
            # Determine separator
            if '：' in line:
                separator = '：'
            elif ':' in line:
                separator = ':'
            else:
                continue
                
            parts = line.split(separator, 1)
            if len(parts) == 2:
                key = parts[0].strip()
                value = parts[1].strip()
                
                # Map file keys to standard keys
                if "Endpoint" in key:
                    credentials["endpoint"] = value
                elif "API Key ID" in key:
                    credentials["api_key"] = value
                elif "Secret Key" in key:
                    credentials["secret_key"] = value
                    
    return credentials
