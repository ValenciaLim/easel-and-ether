import openai
import jinja2
import json
import yaml

class GaiaClient:
    def __init__(self, config):
        self.gaia_url = config.get('gaia_url', 'https://qwen72b.gaia.domains/v1')
        self.gaia_api_key = config.get('gaia_api_key', 'YOUR_API_KEY')
        self.model = config.get('gaia_model', 'llama')
        self.prompt_template_path = config.get('prompt_template', 'prompt_template.j2')
        with open(self.prompt_template_path, 'r') as f:
            self.prompt_template = jinja2.Template(f.read())
        self.client = openai.OpenAI(
            base_url=self.gaia_url,
            api_key=self.gaia_api_key
        )

    async def analyze_asset(self, asset, market_data):
        prompt = self.prompt_template.render(asset=asset, market_data=market_data)
        messages = [
            {"role": "system", "content": "You are a creative, painterly trading agent. Respond ONLY in valid JSON."},
            {"role": "user", "content": prompt}
        ]
        import asyncio
        loop = asyncio.get_event_loop()
        response = await loop.run_in_executor(
            None,
            lambda: self.client.chat.completions.create(
                model=self.model,
                messages=messages,
                temperature=0.7,
                max_tokens=500
            )
        )
        content = response.choices[0].message.content
        try:
            result = json.loads(content)
        except Exception:
            result = {"error": "Failed to parse Gaia response", "raw": content}
        return result

    async def gaia_infer_from_prompt(self, prompt, model=None):
        """
        Send a custom prompt to Gaia and parse the JSON response for asset, action, amount, and reason.
        Returns: dict with keys: asset, action, amount, reason
        """
        messages = [
            {"role": "system", "content": "You are a creative, painterly trading agent. Respond ONLY in valid JSON."},
            {"role": "user", "content": prompt}
        ]
        mdl = model or self.model
        import asyncio
        loop = asyncio.get_event_loop()
        response = await loop.run_in_executor(
            None,
            lambda: self.client.chat.completions.create(
                model=mdl,
                messages=messages,
                temperature=0.7,
                max_tokens=500
            )
        )
        content = response.choices[0].message.content
        try:
            result = json.loads(content)
            asset = result.get('asset')
            action = result.get('action', 'Hold').capitalize()
            amount = result.get('amount', 1)
            reason = result.get('reason', '')
        except Exception:
            asset = None
            action = 'Hold'
            amount = 1
            reason = f"Failed to parse Gaia response: {content}"
        return {"asset": asset, "action": action, "amount": amount, "reason": reason}

# Load config for GaiaClient singleton
with open('config.yaml') as f:
    config = yaml.safe_load(f)

gaia_client = GaiaClient({
    'gaia_url': config.get('gaia_url', 'https://YOUR-GAIA-DOMAIN.gaia.domains/v1'),
    'gaia_api_key': config['api_keys']['gaia'],
    'gaia_model': config.get('gaia_model', 'llama'),
    'prompt_template': 'prompt_template.j2'
})

import asyncio

def get_gaia_trade_signal(symbol, visual_desc):
    """
    Send the painterly description to Gaia and receive a trade recommendation.
    Returns: (asset, action, amount, reasoning)
    """
    market_data = visual_desc
    loop = asyncio.get_event_loop()
    result = loop.run_until_complete(gaia_client.analyze_asset(symbol, market_data))
    if isinstance(result, dict):
        asset = result.get('asset', symbol)
        action = result.get('action', 'Hold').capitalize()
        amount = result.get('amount', 1)
        reasoning = result.get('reason', visual_desc)
    else:
        asset = symbol
        action = 'Hold'
        amount = 1
        reasoning = visual_desc
    return asset, action, amount, reasoning 