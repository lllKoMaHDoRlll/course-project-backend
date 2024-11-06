from pytoniq_core import Address # type: ignore
from tonutils.client import TonapiClient # type: ignore
from tonutils.nft import CollectionEditableModified # type: ignore
from tonutils.nft.content import NFTModifiedOnchainContent # type: ignore
from tonutils.wallet import WalletV5R1, WalletV4R2 # type: ignore

import os
from dotenv import load_dotenv

load_dotenv()

IS_TESTNET = True

class TON:
    def __init__(self):
        self.TONAPI_KEY = os.environ.get("TONAPI_KEY")
        self.TON_MNEMONIC = os.environ.get("TON_MNEMONIC")
        self.TON_OWNER_ADDRESS = os.environ.get("TON_OWNER_ADDR")
        self.TON_COLLECTION_ADDRESS = os.environ.get("TON_COLLECTION_ADDR")
        if (any(map(lambda x: x is None, [self.TONAPI_KEY, self.TON_MNEMONIC, self.TON_OWNER_ADDRESS, self.TON_COLLECTION_ADDRESS]))):
            raise KeyError()
        self.TON_MNEMONIC = self.TON_MNEMONIC.split()

        self.client = TonapiClient(api_key=self.TONAPI_KEY, is_testnet=IS_TESTNET)
        self.wallet, _, _, _ = WalletV4R2.from_mnemonic(self.client, self.TON_MNEMONIC)

    async def get_next_nft_index(self) -> int:
        try:
            res = await self.client.run_get_method(address=self.TON_COLLECTION_ADDRESS, method_name="get_collection_data")
            return int(res["stack"][0]["num"], 16)
        except Exception as ex:
            print(ex)
            return -1

    async def mint_sbt(self, owner_address: str, name: str, description: str, image_url: str, attributes: list[dict[str, str]]) -> str:
        nft_index = await self.get_next_nft_index()
        if nft_index == -1:
            return ""

        try:
            body = CollectionEditableModified.build_mint_body(
                index=nft_index,
                owner_address=owner_address,
                content=NFTModifiedOnchainContent(
                    name=name,
                    description=description,
                    image=image_url,
                    attributes=attributes
                )
            )

            tx_hash = await self.wallet.transfer(
                destination=self.TON_COLLECTION_ADDRESS,
                amount=0.05,
                body=body
            )
            return tx_hash
        except Exception as ex:
            print(ex)
            return ""


ton = TON()
