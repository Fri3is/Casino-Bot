import aiohttp
import asyncio
from typing import Optional, Dict
import json
import hashlib
import hmac
import time

class CryptoPayAPI:
    def __init__(self, token: str):
        self.token = token
        self.base_url = "https://pay.crypt.bot/api"
        
    def _get_headers(self):
        """Get headers for API requests"""
        return {
            "Crypto-Pay-API-Token": self.token,
            "Content-Type": "application/json"
        }
    
    async def create_invoice(self, amount: float, currency: str = "USDT", 
                           description: str = "Пополнение баланса", user_id: int = None) -> Optional[Dict]:
        """Create payment invoice"""
        async with aiohttp.ClientSession() as session:
            payload = {
                "amount": str(amount),
                "asset": currency,
                "description": description,
                "hidden_message": f"Пополнение для пользователя {user_id}" if user_id else None
            }
            
            try:
                async with session.post(
                    f"{self.base_url}/createInvoice",
                    headers=self._get_headers(),
                    json=payload
                ) as response:
                    if response.status == 200:
                        data = await response.json()
                        if data.get("ok"):
                            return data.get("result")
                    return None
            except Exception as e:
                print(f"Error creating invoice: {e}")
                return None
    
    async def get_invoice(self, invoice_id: str) -> Optional[Dict]:
        """Get invoice information"""
        async with aiohttp.ClientSession() as session:
            try:
                async with session.get(
                    f"{self.base_url}/getInvoices",
                    headers=self._get_headers(),
                    params={"invoice_ids": invoice_id}
                ) as response:
                    if response.status == 200:
                        data = await response.json()
                        if data.get("ok") and data.get("result", {}).get("items"):
                            return data["result"]["items"][0]
                    return None
            except Exception as e:
                print(f"Error getting invoice: {e}")
                return None
    
    async def get_balance(self) -> Optional[Dict]:
        """Get bot balance"""
        async with aiohttp.ClientSession() as session:
            try:
                async with session.get(
                    f"{self.base_url}/getBalance",
                    headers=self._get_headers()
                ) as response:
                    if response.status == 200:
                        data = await response.json()
                        if data.get("ok"):
                            return data.get("result")
                    return None
            except Exception as e:
                print(f"Error getting balance: {e}")
                return None
    
    async def transfer(self, user_id: int, amount: float, currency: str = "USDT", 
                      comment: str = "Вывод средств") -> Optional[Dict]:
        """Transfer funds to user"""
        async with aiohttp.ClientSession() as session:
            payload = {
                "user_id": user_id,
                "amount": str(amount),
                "asset": currency,
                "comment": comment
            }
            
            try:
                async with session.post(
                    f"{self.base_url}/transfer",
                    headers=self._get_headers(),
                    json=payload
                ) as response:
                    if response.status == 200:
                        data = await response.json()
                        if data.get("ok"):
                            return data.get("result")
                    return None
            except Exception as e:
                print(f"Error making transfer: {e}")
                return None
    
    async def get_currencies(self) -> Optional[Dict]:
        """Get supported currencies"""
        async with aiohttp.ClientSession() as session:
            try:
                async with session.get(
                    f"{self.base_url}/getCurrencies",
                    headers=self._get_headers()
                ) as response:
                    if response.status == 200:
                        data = await response.json()
                        if data.get("ok"):
                            return data.get("result")
                    return None
            except Exception as e:
                print(f"Error getting currencies: {e}")
                return None