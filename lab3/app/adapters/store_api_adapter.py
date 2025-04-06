import json
import logging
from typing import List
from datetime import datetime

import pydantic_core
import requests

from app.entities.processed_agent_data import ProcessedAgentData
from app.interfaces.store_gateway import StoreGateway


class StoreApiAdapter(StoreGateway):
    def __init__(self, api_base_url):
        self.api_base_url = api_base_url

    def save_data(self, processed_agent_data_batch: List[ProcessedAgentData]):
        endpoint = f"{self.api_base_url}/processed_agent_data"
        success = True

        for item in processed_agent_data_batch:
            try:
                # Перетворюємо модель в словник
                data = item.model_dump(mode='json')

                # Перетворюємо timestamp з рядка в ціле число
                if isinstance(data["agent_data"]["timestamp"], str):
                    timestamp_str = data["agent_data"]["timestamp"]
                    dt = datetime.fromisoformat(timestamp_str.replace('Z', '+00:00'))
                    data["agent_data"]["timestamp"] = int(dt.timestamp() * 1000)

                # Відправка даних
                response = requests.post(endpoint, json=data)

                if response.status_code != 200:
                    logging.error(f"Failed to save item to Store API: {response.status_code}, {response.text}")
                    success = False
                else:
                    logging.info(f"Successfully saved item to Store API")

            except Exception as e:
                logging.error(f"Failed to save item to Store API: {str(e)}")
                success = False

        return success



