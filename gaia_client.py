import openai
import jinja2
import json

class GaiaClient:
    def __init__(self, config):
        self.gaia_url = config.get('gaia_url', 'https://YOUR-GAIA-DOMAIN.gaia.domains/v1')
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
            {"role": "system", "content": "You are a narrative-driven, contrarian market psychologist. Respond ONLY in valid JSON."},
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