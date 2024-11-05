import re
import requests
import plotly.graph_objects as go
import json
from typing import Dict, Optional, List
from datetime import datetime

def is_valid_btc_address(address: str) -> bool:
    """Validate Bitcoin address format."""
    pattern = r'^(1|3|bc1)[a-zA-Z0-9]{25,62}$'
    return bool(re.match(pattern, address))

def get_address_info(address: str) -> Optional[Dict]:
    """Fetch address information from BlockCypher API."""
    try:
        response = requests.get(f'https://api.blockcypher.com/v1/btc/main/addrs/{address}')
        if response.status_code == 200:
            data = response.json()
            return {
                'balance': data.get('balance', 0) / 100000000,  # Convert satoshis to BTC
                'total_received': data.get('total_received', 0) / 100000000,
                'total_sent': data.get('total_sent', 0) / 100000000,
                'n_tx': data.get('n_tx', 0)
            }
    except requests.RequestException as e:
        print(f"Request failed: {e}")  # 오류 메시지 로깅
        return None
    return None

def get_detailed_transactions(address: str, limit: int = 10) -> Optional[List[Dict]]:
    """Fetch detailed transaction data for an address."""
    try:
        response = requests.get(
            f'https://api.blockcypher.com/v1/btc/main/addrs/{address}/full',
            params={'limit': limit})
        if response.status_code == 200:
            data = response.json()
            return data.get('txs', [])
    except requests.RequestException as e:
        print(f"Request failed: {e}")  # 오류 메시지 로깅
        return None
    return None

def truncate_address(address: str, length: int = 8) -> str:
    """Truncate address for display while keeping start and end."""
    if len(address) <= length:
        return address
    return f"{address[:length//2]}...{address[-length//2:]}"

def create_transaction_flow_visualization(transactions: List[Dict], address: str) -> Optional[str]:
    """Create a Sankey diagram for transaction flow visualization."""
    if not transactions:
        return None

    # Prepare nodes and links data
    nodes = {address: 0}
    node_labels = [truncate_address(address)]
    links_source = []
    links_target = []
    links_value = []
    links_color = []

    for tx in transactions:
        tx_hash = tx.get('hash', '')[:8]

        # Process each input address
        for inp in tx.get('inputs', []):
            addr = inp.get('addresses', [None])[0]
            if addr and addr != address:
                if addr not in nodes:
                    nodes[addr] = len(node_labels)
                    node_labels.append(truncate_address(addr))
                links_source.append(nodes[addr])
                links_target.append(0)
                value = inp.get('output_value', 0) / 100000000
                links_value.append(value)
                links_color.append('rgba(255, 65, 54, 0.8)')

        # Process each output address
        for out in tx.get('outputs', []):
            addr = out.get('addresses', [None])[0]
            if addr and addr != address:
                if addr not in nodes:
                    nodes[addr] = len(node_labels)
                    node_labels.append(truncate_address(addr))
                links_source.append(0)
                links_target.append(nodes[addr])
                value = out.get('value', 0) / 100000000
                links_value.append(value)
                links_color.append('rgba(0, 116, 217, 0.8)')

    fig = go.Figure(data=[
        go.Sankey(
            node=dict(
                pad=15,
                thickness=20,
                line=dict(color="black", width=0.5),
                label=node_labels,
                color="rgba(128, 128, 128, 0.4)"),
            link=dict(source=links_source,
                      target=links_target,
                      value=links_value,
                      color=links_color))
    ])

    fig.update_layout(
        title=dict(
            text="Transaction Flow Visualization",
            font=dict(size=14)
        ),
        font_size=12,
        width=0.9 * 1024,
        height=0.6 * 768,
        template="plotly_dark",
        hoverlabel=dict(bgcolor="white", font_size=12, font_family="monospace"),
        margin=dict(t=30, l=30, r=30, b=30)
    )

    return json.dumps(fig.to_dict())

def sanitize_address(address: str) -> str:
    """Sanitize input address."""
    return address.strip()