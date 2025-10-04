#!/usr/bin/env python3
"""
Flask web application for getting earliest token transactions
"""
import random
import requests
import json
import os
import time
from datetime import datetime
from flask import Flask, render_template, request, jsonify, send_file, url_for

app = Flask(__name__)

# Enable template auto-reloading for development
app.config['TEMPLATES_AUTO_RELOAD'] = True
app.config['SEND_FILE_MAX_AGE_DEFAULT'] = 0

# Configure upload folder for JSON files
DOWNLOAD_FOLDER = 'downloads'
if not os.path.exists(DOWNLOAD_FOLDER):
    os.makedirs(DOWNLOAD_FOLDER)

def generate_solauth_token() -> str:
    """
    Generate a valid sol-aut token used to authenticate requests to the Solscan API.
    """
    chars = "abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789==--"
    t = "".join(random.choice(chars) for _ in range(16))
    r = "".join(random.choice(chars) for _ in range(16))
    n = random.randint(0, 31)
    i = t + r
    return i[:n] + "B9dls0fK" + i[n:]


def get_historical_transactions_by_block(token_address, count=100):
    """Get earliest transactions by collecting historical data and sorting by block_id"""
    
    logs = []
    logs.append(f"🚀 Getting earliest {count} transactions for: {token_address}")
    logs.append("Using block_id sorting method (lower block_id = older transaction)")
    logs.append("=" * 70)
    
    base_url = "https://api-v2.solscan.io/v2"
    headers = {
        "Accept": "application/json, text/plain, */*",
        "sol-aut": generate_solauth_token(),
        "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36",
        "Referer": "https://solscan.io/",
        "Origin": "https://solscan.io",
        "Connection": "keep-alive",
    }
    
    all_transactions = []
    
    # Get historical data from different time periods
    # Use early Solana dates to get old transactions
    historical_dates = [
        datetime(2020, 3, 16),  # Solana mainnet launch
        datetime(2020, 6, 1),
        datetime(2020, 9, 1),
        datetime(2021, 1, 1),
        datetime(2021, 6, 1),
        datetime(2021, 12, 1),
        datetime(2022, 6, 1),
        datetime(2023, 1, 1),
    ]
    
    for target_date in historical_dates:
        if len(all_transactions) >= count * 5:  # Get more than needed
            break
            
        logs.append(f"\n📅 Searching before: {target_date.strftime('%Y-%m-%d')}")
        
        # Get multiple pages for each date
        for page in range(1, 6):  # Max 5 pages per date
            params = {
                "address": token_address,
                "page": page,
                "page_size": 100,
                "to_time": int(target_date.timestamp())
            }
            
            try:
                response = requests.get(
                    f"{base_url}/token/transfer",
                    headers=headers,
                    params=params,
                    timeout=15
                )
                
                if response.status_code == 200:
                    data = response.json()
                    if data.get('success') and data.get('data'):
                        transactions = data['data']
                        
                        # Filter out duplicates by trans_id
                        new_transactions = []
                        existing_ids = {tx.get('trans_id') for tx in all_transactions}
                        
                        for tx in transactions:
                            tx_id = tx.get('trans_id')
                            if tx_id and tx_id not in existing_ids:
                                new_transactions.append(tx)
                                existing_ids.add(tx_id)
                        
                        all_transactions.extend(new_transactions)
                        logs.append(f"   Page {page}: Got {len(new_transactions)} new transactions")
                        
                        if len(transactions) < 100:  # Last page for this date
                            break
                    else:
                        logs.append(f"   Page {page}: No data")
                        break
                else:
                    logs.append(f"   Page {page}: HTTP {response.status_code}")
                    break
            except Exception as e:
                logs.append(f"   Page {page}: Error - {e}")
                break
    
    logs.append(f"\n📊 PROCESSING COLLECTED DATA")
    logs.append("=" * 70)
    logs.append(f"Total transactions collected: {len(all_transactions)}")
    
    # Sort by block_id (ascending = oldest first)
    all_transactions.sort(key=lambda x: x.get('block_id', float('inf')))
    
    # Return earliest transactions
    earliest_transactions = all_transactions[:count]
    
    logs.append(f"Returning earliest: {len(earliest_transactions)}")
    
    if earliest_transactions:
        oldest = earliest_transactions[0]
        newest = earliest_transactions[-1]
        
        oldest_block = oldest.get('block_id', 0)
        newest_block = newest.get('block_id', 0)
        
        logs.append(f"📦 Oldest block: {oldest_block:,}")
        logs.append(f"📦 Newest block in selection: {newest_block:,}")
        logs.append(f"📈 Block range: {newest_block - oldest_block:,} blocks")
        logs.append(f"🔗 Oldest TX ID: {oldest.get('trans_id', 'N/A')}")
        logs.append(f"💰 Oldest TX amount: {oldest.get('amount', 0):,} tokens")
        
        # Analyze data
        block_ids = [tx.get('block_id', 0) for tx in earliest_transactions]
        amounts = [tx.get('amount', 0) for tx in earliest_transactions]
        
        logs.append(f"\n📈 STATISTICS:")
        logs.append(f"   Block ID range: {min(block_ids):,} - {max(block_ids):,}")
        logs.append(f"   Amount range: {min(amounts):,} - {max(amounts):,} tokens")
        
        # Activity types
        activity_types = {}
        for tx in earliest_transactions:
            activity_type = tx.get('activity_type', 'Unknown')
            activity_types[activity_type] = activity_types.get(activity_type, 0) + 1
        
        logs.append(f"   Activity types:")
        for activity, count in sorted(activity_types.items(), key=lambda x: x[1], reverse=True):
            logs.append(f"     {activity}: {count}")
        
        # Save to file with timestamp
        timestamp = int(time.time())
        filename = f"E-{timestamp}.json"
        filepath = os.path.join(DOWNLOAD_FOLDER, filename)
        
        data = {
            "token_address": token_address,
            "search_method": "historical_block_id_sorting",
            "fetched_at": datetime.now().isoformat(),
            "total_count": len(earliest_transactions),
            "block_range": {
                "earliest_block": oldest_block,
                "latest_block": newest_block,
                "block_span": newest_block - oldest_block
            },
            "transactions": earliest_transactions
        }
        
        with open(filepath, 'w') as f:
            json.dump(data, f, indent=2)
        
        logs.append(f"\n💾 Earliest transactions saved to: {filename}")
        
        # Print first few transactions as examples
        logs.append(f"\n🔍 FIRST 5 TRANSACTIONS:")
        for i, tx in enumerate(earliest_transactions[:5]):
            logs.append(f"   {i+1}. Block: {tx.get('block_id', 0):,} | Amount: {tx.get('amount', 0):,} | TX: {tx.get('trans_id', 'N/A')[:20]}...")
    
    return earliest_transactions, logs, filename if earliest_transactions else None

@app.route('/')
def index():
    """Main page with form"""
    return render_template('index.html')

@app.route('/process', methods=['POST'])
def process_request():
    """Process the form submission and return results"""
    try:
        token_address = request.form.get('token_address', '').strip()
        count = int(request.form.get('count', 100))
        
        if not token_address:
            return jsonify({
                'success': False,
                'error': 'Token address is required'
            })
        
        if count <= 0 or count > 1000:
            return jsonify({
                'success': False,
                'error': 'Count must be between 1 and 1000'
            })
        
        # Process the request
        transactions, logs, filename = get_historical_transactions_by_block(token_address, count)
        
        if transactions and filename:
            # Get the latest file (should be the one we just created)
            download_url = url_for('download_file', filename=filename)
            
            return jsonify({
                'success': True,
                'message': f'Successfully found {len(transactions)} earliest transactions!',
                'download_url': download_url,
                'filename': filename,
                'logs': logs,
                'transaction_count': len(transactions)
            })
        else:
            return jsonify({
                'success': False,
                'error': 'No transactions found',
                'logs': logs
            })
            
    except ValueError:
        return jsonify({
            'success': False,
            'error': 'Invalid count value. Please enter a number.'
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'error': f'An error occurred: {str(e)}'
        })

@app.route('/download/<filename>')
def download_file(filename):
    """Download the generated JSON file"""
    try:
        filepath = os.path.join(DOWNLOAD_FOLDER, filename)
        if os.path.exists(filepath):
            return send_file(filepath, as_attachment=True, download_name=filename)
        else:
            return "File not found", 404
    except Exception as e:
        return f"Error downloading file: {str(e)}", 500

@app.route('/api/token/search')
def search_tokens():
    """Advanced token search using real Solscan API"""
    keyword = request.args.get('keyword', '').strip()
    category = request.args.get('category', 'all').lower()  # all, tokens, addresses
    
    if not keyword or len(keyword) < 2:
        return jsonify({
            "success": True,
            "data": {
                "all": [],
                "tokens": [],
                "addresses": [],
                "total_count": 0
            }
        })
    
    print(f"🔍 Searching Solscan API for: {keyword} (category: {category})")
    
    # Get real data from Solscan API
    real_tokens = get_real_token_results(keyword)
    real_addresses = get_real_address_results(keyword)
    
    # Filter based on category
    if category == 'tokens':
        return jsonify({
            "success": True,
            "data": {
                "tokens": real_tokens,
                "total_count": len(real_tokens)
            }
        })
    elif category == 'addresses':
        return jsonify({
            "success": True,
            "data": {
                "addresses": real_addresses,
                "total_count": len(real_addresses)
            }
        })
    else:  # all
        all_results = real_tokens + real_addresses
        return jsonify({
            "success": True,
            "data": {
                "all": all_results,
                "tokens": real_tokens,
                "addresses": real_addresses,
                "total_count": len(all_results)
            }
        })

def get_real_token_results(keyword):
    """Get real token results from Solscan v2 search API"""
    try:
        headers = {
            "Accept": "application/json, text/plain, */*",
            "sol-aut": generate_solauth_token(),
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
            "Referer": "https://solscan.io/",
            "Origin": "https://solscan.io",
            "Connection": "keep-alive",
        }
        
        # Use the correct Solscan v2 search API
        url = "https://api-v2.solscan.io/v2/search"
        params = {"keyword": keyword}
        
        print(f"   🔍 Searching tokens with v2 API: {keyword}")
        response = requests.get(url, headers=headers, params=params, timeout=15)
        
        print(f"   Status: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            
            if data.get('success') and data.get('data'):
                tokens = []
                
                # Find tokens group in response
                for group in data['data']:
                    if group.get('type') == 'tokens' and 'result' in group:
                        for token in group['result'][:20]:  # Limit to 20
                            normalized_token = {
                                "type": "token",
                                "address": token.get('address', ''),
                                "symbol": token.get('symbol', 'UNKNOWN'),
                                "name": token.get('name', 'Unknown Token'),
                                "logoUri": token.get('icon', ''),
                                "verified": token.get('reputation', '') == 'ok',
                                "decimals": token.get('decimals', 9),
                                "holders": token.get('holder', 0),
                                "priority": token.get('priority', 0)
                            }
                            
                            if normalized_token['address'] and len(normalized_token['address']) > 20:
                                tokens.append(normalized_token)
                
                print(f"   ✅ Found {len(tokens)} tokens")
                return tokens
            else:
                print(f"   ❌ No success or data in response")
                return []
        else:
            print(f"   ❌ HTTP {response.status_code}: {response.text[:200]}")
            return []
            
    except Exception as e:
        print(f"❌ Token search error: {str(e)}")
        return []

def get_real_address_results(keyword):
    """Get real address results from the same v2 search API"""
    try:
        headers = {
            "Accept": "application/json, text/plain, */*",
            "sol-aut": generate_solauth_token(),
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
            "Referer": "https://solscan.io/",
            "Origin": "https://solscan.io",
            "Connection": "keep-alive",
        }
        
        # Use the same v2 search API for addresses
        url = "https://api-v2.solscan.io/v2/search"
        params = {"keyword": keyword}
        
        print(f"   🔍 Searching addresses with v2 API: {keyword}")
        response = requests.get(url, headers=headers, params=params, timeout=15)
        
        if response.status_code == 200:
            data = response.json()
            
            if data.get('success') and data.get('data'):
                addresses = []
                
                # Find addresses/accounts group in response
                for group in data['data']:
                    if group.get('type') == 'address' and 'result' in group:
                        for addr in group['result'][:20]:  # Limit to 20
                            normalized_address = {
                                "type": "address",
                                "address": addr.get('address', ''),
                                "label": addr.get('label') or addr.get('name') or 'Unknown Address',
                                "description": addr.get('description', '')
                            }
                            
                            if normalized_address['address'] and len(normalized_address['address']) > 20:
                                addresses.append(normalized_address)
                
                print(f"   ✅ Found {len(addresses)} addresses")
                return addresses
            else:
                return []
        else:
            return []
            
    except Exception as e:
        print(f"❌ Address search error: {str(e)}")
        return []

@app.route('/latest')
def get_latest_file():
    """Get the latest generated file for download"""
    try:
        files = [f for f in os.listdir(DOWNLOAD_FOLDER) if f.startswith('E-') and f.endswith('.json')]
        if files:
            # Sort by timestamp (filename contains timestamp)
            files.sort(key=lambda x: int(x.split('-')[1].split('.')[0]), reverse=True)
            latest_file = files[0]
            return download_file(latest_file)
        else:
            return "No files available", 404
    except Exception as e:
        return f"Error: {str(e)}", 500

if __name__ == "__main__":
    port = int(os.environ.get('PORT', 5001))
    app.run(debug=False, host='0.0.0.0', port=port)
else:
    print("Flask app imported as a module")