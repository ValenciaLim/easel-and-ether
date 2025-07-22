import httpx

class RecallSandboxClient:
    def __init__(self, config):
        self.api_url = config.get('recall_api_url', 'https://api.sandbox.competitions.recall.network/api')
        self.api_key = config.get('recall_api_key', 'YOUR_RECALL_API_KEY')
        self.headers = {
            'Authorization': f'Bearer {self.api_key}',
            'Content-Type': 'application/json',
            'Accept': 'application/json',
        }

    async def get_token_price(self, token, chain=None, specific_chain=None):
        # GET /api/price
        params = {'token': token}
        if chain:
            params['chain'] = chain
        if specific_chain:
            params['specificChain'] = specific_chain
        url = f"{self.api_url}/price"
        async with httpx.AsyncClient() as client:
            resp = await client.get(url, headers=self.headers, params=params)
            resp.raise_for_status()
            return resp.json()

    async def get_token_info(self, token, chain=None, specific_chain=None):
        # GET /api/price/token-info
        params = {'token': token}
        if chain:
            params['chain'] = chain
        if specific_chain:
            params['specificChain'] = specific_chain
        url = f"{self.api_url}/price/token-info"
        async with httpx.AsyncClient() as client:
            resp = await client.get(url, headers=self.headers, params=params)
            resp.raise_for_status()
            return resp.json()

    async def get_trade_quote(self, from_token, to_token, amount, from_chain=None, from_specific_chain=None, to_chain=None, to_specific_chain=None):
        # GET /api/trade/quote
        params = {
            'fromToken': from_token,
            'toToken': to_token,
            'amount': str(amount)
        }
        if from_chain:
            params['fromChain'] = from_chain
        if from_specific_chain:
            params['fromSpecificChain'] = from_specific_chain
        if to_chain:
            params['toChain'] = to_chain
        if to_specific_chain:
            params['toSpecificChain'] = to_specific_chain
        url = f"{self.api_url}/trade/quote"
        async with httpx.AsyncClient() as client:
            resp = await client.get(url, headers=self.headers, params=params)
            resp.raise_for_status()
            return resp.json()

    async def execute_trade(self, from_token, to_token, amount, reason, slippage_tolerance, from_chain, from_specific_chain, to_chain, to_specific_chain):
        # POST /api/trade/execute
        url = f"{self.api_url}/trade/execute"
        payload = {
            'fromToken': from_token,
            'toToken': to_token,
            'amount': str(amount),
            'reason': reason,
            'slippageTolerance': str(slippage_tolerance),
            'fromChain': from_chain,
            'fromSpecificChain': from_specific_chain,
            'toChain': to_chain,
            'toSpecificChain': to_specific_chain
        }
        async with httpx.AsyncClient() as client:
            resp = await client.post(url, headers=self.headers, json=payload)
            resp.raise_for_status()
            return resp.json()

    async def get_portfolio(self):
        # GET /agent/portfolio
        url = f"{self.api_url}/agent/portfolio"
        async with httpx.AsyncClient() as client:
            resp = await client.get(url, headers=self.headers)
            resp.raise_for_status()
            return resp.json() 