"""
nft_ctrt contains NFT contract.
"""
from __future__ import annotations
from typing import Dict, Any, TYPE_CHECKING

from loguru import logger

# https://stackoverflow.com/a/39757388
if TYPE_CHECKING:
    from py_v_sdk import account as acnt

from py_v_sdk import data_entry as de
from py_v_sdk import tx_req as tx
from py_v_sdk import model as md

from . import CtrtMeta, Ctrt


class NFTCtrt(Ctrt):
    """
    NFTCtrt is the class for VSYS NFT contract V1
    """

    CTRT_META = CtrtMeta.from_b58_str(
        "VJodouhmnHVDwtkBZ2NdgahT7NAgNE9EpWoZApzobhpua2nDL9D3sbHSoRRk8bEFeme2BHrXPdcq5VNJcPdGMUD54Smwatyx74cPJyet6bCWmLciHE2jGw9u5TmatjdpFSjGKegh76GvJstK3VaLagvsJJMaaKM9MNXYtgJyDr1Zw7U9PXV7N9TQnSsqz6EHMgDvd8aTDqEG7bxxAotkAgeh4KHqnk6Ga117q5AJctJcbUtD99iUgPmJrC8vzX85TEXgHRY1psW7D6daeExfVVrEPHFHrU6XfhegKv9vRbJBGL861U4Qg6HWbWxbuitgtKoBazSp7VofDtrZebq2NSpZoXCAZC8DRiaysanAqyCJZf7jJ8NfXtWej8L9vg8PVs65MrEmK8toadcyCA2UGzg6pQKrMKQEUahruBiS7zuo62eWwJBxUD1fQ1RGPk9BbMDk9FQQxXu3thSJPnKktq3aJhD9GNFpvyEAaWigp5nfjgH5doVTQk1PgoxeXRAWQNPztjNvZWv6iD85CoZqfCWdJbAXPrWvYW5FsRLW1xJ4ELRUfReMAjCGYuFWdA3CZyefpiDEWqVTe5SA6J6XeUppRyXKpKQTc6upesoAGZZ2NtFDryq22izC6D5p1i98YpC6Dk1qcKevaANKHH8TfFoQT717nrQEY2aLoWrA1ip2t5etdZjNVFmghxXEeCAGy3NcLDFHmAfcBZhHKeJHp8H8HbiMRtWe3wmwKX6mPx16ahnd3dMGCsxAZfjQcy4J1HpuCm7rHMULkixUFYRYqx85c7UpLcijLRybE1MLRjEZ5SEYtazNuiZBwq1KUcNipzrxta9Rpvt2j4WyMadxPf5r9YeAaJJp42PiC6SGfyjHjRQN4K3pohdQRbbG4HQ95NaWCy7CAwbpXRCh9NDMMQ2cmTfB3KFW2M"
    )

    class FuncIdx(Ctrt.FuncIdx):
        """
        FuncIdx is the enum class for function indexes of a contract.
        """

        SUPERSEDE = 0
        ISSUE = 1
        SEND = 2
        TRANSFER = 3
        DEPOSIT = 4
        WITHDRAW = 5

    class StateVar(Ctrt.StateVar):
        """
        StateVar is the enum class for state variables of a contract.
        """

        ISSUER = 0
        MAKER = 1

    class DBKey(Ctrt.DBKey):
        """
        DBKey is the class for DB key of a contract used to query data.
        """

        @classmethod
        def for_issuer(cls) -> NFTCtrt.DBKey:
            """
            for_issuer returns the NFTCtrt.DBKey object for querying the issuer.

            Returns:
                NFTCtrt.DBKey: The NFTCtrt.DBKey object.
            """
            b = NFTCtrt.StateVar.ISSUER.serialize()
            return cls(b)

        @classmethod
        def for_maker(cls) -> NFTCtrt.DBKey:
            """
            for_maker returns the NFTCtrt.DBKey object for querying the maker.

            Returns:
                NFTCtrt.DBKey: The NFTCtrt.DBKey object.
            """
            b = NFTCtrt.StateVar.MAKER.serialize()
            return cls(b)

    @classmethod
    def register(
        cls,
        by: acnt.Account,
        description: str = "",
        fee: int = md.RegCtrtFee.DEFAULT,
    ) -> NFTCtrt:
        """
        register registers an NFT Contract.

        Args:
            by (acnt.Account): The action taker.
            description (str, optional): The description of the action. Defaults to "".
            fee (int, optional): The fee to pay for this action. Defaults to md.RegCtrtFee.DEFAULT.

        Returns:
            NFTCtrt: The NFTCtrt object of the registered NFT contract.
        """
        data = by.register_contract(
            tx.RegCtrtTxReq(
                data_stack=de.DataStack(),
                ctrt_meta=cls.CTRT_META,
                timestamp=md.VSYSTimestamp.now(),
                description=md.Str(description),
                fee=md.RegCtrtFee(fee),
            )
        )
        logger.debug(data)

        return cls(
            data["contractId"],
            chain=by.chain,
        )

    @property
    def issuer(self) -> str:
        """
        issuer queries & returns the issuer of the contract.

        Returns:
            str: The address of the issuer of the contract.
        """
        data = self.chain.api.ctrt.get_ctrt_data(
            ctrt_id=self.ctrt_id,
            db_key=self.DBKey.for_issuer().b58_str,
        )
        logger.debug(data)
        return data["value"]

    @property
    def maker(self) -> str:
        """
        maker queries & returns the maker of the contract.

        Returns:
            str: The address of the maker of the contract.
        """
        data = self.chain.api.ctrt.get_ctrt_data(
            ctrt_id=self.ctrt_id,
            db_key=self.DBKey.for_maker().b58_str,
        )
        logger.debug(data)
        return data["value"]

    def issue(
        self,
        by: acnt.Account,
        attachment: str = "",
        fee: int = md.ExecCtrtFee.DEFAULT,
    ) -> Dict[str, Any]:
        """
        issue issues a token of the NFT contract.

        Args:
            by (acnt.Account): The action taker.
            attachment (str, optional): The attachment of the action. Defaults to "".
            fee (int, optional): The fee to pay for this action. Defaults to md.ExecCtrtFee.DEFAULT.

        Returns:
            Dict[str, Any]: The response returned by the Node API
        """
        data = by.execute_contract(
            tx.ExecCtrtFuncTxReq(
                ctrt_id=self._ctrt_id,
                func_id=self.FuncIdx.ISSUE,
                data_stack=de.DataStack(
                    de.String(md.Str(attachment)),
                ),
                timestamp=md.VSYSTimestamp.now(),
                attachment=md.Str(attachment),
                fee=md.ExecCtrtFee(fee),
            )
        )
        logger.debug(data)
        return data

    def send(
        self,
        by: acnt.Account,
        recipient: str,
        tok_idx: int,
        attachment: str = "",
        fee: int = md.ExecCtrtFee.DEFAULT,
    ) -> Dict[str, Any]:
        """
        send sends the NFT token from the action taker to the recipient.

        Args:
            by (acnt.Account): The action taker.
            recipient (str): The account address of the recipient.
            tok_idx (int): The index of the token within this contract to send.
            attachment (str, optional): The attachment of the action. Defaults to "".
            fee (int, optional): The fee to pay for this action. Defaults to md.ExecCtrtFee.DEFAULT.

        Returns:
            Dict[str, Any]: The response returned by the Node API
        """

        rcpt_md = md.Addr(recipient)
        rcpt_md.must_on(by.chain)

        data = by.execute_contract(
            tx.ExecCtrtFuncTxReq(
                ctrt_id=self._ctrt_id,
                func_id=self.FuncIdx.SEND,
                data_stack=de.DataStack(
                    de.Addr(rcpt_md),
                    de.INT32(md.TokenIdx(tok_idx)),
                ),
                timestamp=md.VSYSTimestamp.now(),
                attachment=md.Str(attachment),
                fee=md.ExecCtrtFee(fee),
            )
        )
        logger.debug(data)
        return data

    def transfer(
        self,
        by: acnt.Account,
        sender: str,
        recipient: str,
        tok_idx: int,
        attachment: str = "",
        fee: int = md.ExecCtrtFee.DEFAULT,
    ) -> Dict[str, Any]:
        """
        transfer transfers the NFT token from the sender to the recipient.

        Args:
            by (acnt.Account): The action taker.
            sender (str): The account address of the sender.
            recipient (str): The account address of the recipient.
            tok_idx (int): The index of the token within this contract to transfer.
            attachment (str, optional): The attachment of this action. Defaults to "".
            fee (int, optional): The fee to pay for this action. Defaults to md.ExecCtrtFee.DEFAULT.

        Returns:
            Dict[str, Any]: The response returned by the Node API
        """
        sender_md = md.Addr(sender)
        rcpt_md = md.Addr(recipient)

        sender_md.must_on(by.chain)
        rcpt_md.must_on(by.chain)

        data = by.execute_contract(
            tx.ExecCtrtFuncTxReq(
                ctrt_id=self._ctrt_id,
                func_id=self.FuncIdx.TRANSFER,
                data_stack=de.DataStack(
                    de.Addr(sender_md),
                    de.Addr(rcpt_md),
                    de.INT32(md.TokenIdx(tok_idx)),
                ),
                timestamp=md.VSYSTimestamp.now(),
                attachment=md.Str(attachment),
                fee=md.ExecCtrtFee(fee),
            )
        )
        logger.debug(data)
        return data

    def deposit(
        self,
        by: acnt.Account,
        ctrt_id: str,
        tok_idx: int,
        attachment: str = "",
        fee: int = md.ExecCtrtFee.DEFAULT,
    ) -> Dict[str, Any]:
        """
        deposit deposits the NFT token from the action taker to another contract.

        Args:
            by (acnt.Account): The action taker.
            ctrt_id (str): The id of the contract to deposit into.
            tok_idx (int): The index of the token within this contract to deposit.
            attachment (str, optional): The attachment of this action. Defaults to "".
            fee (int, optional): The fee to pay for this action. Defaults to md.ExecCtrtFee.DEFAULT.

        Returns:
            Dict[str, Any]: The response returned by the Node API
        """
        data = by.execute_contract(
            tx.ExecCtrtFuncTxReq(
                ctrt_id=self._ctrt_id,
                func_id=self.FuncIdx.DEPOSIT,
                data_stack=de.DataStack(
                    de.Addr(md.Addr(by.addr.b58_str)),
                    de.CtrtAcnt(md.CtrtID(ctrt_id)),
                    de.INT32(md.TokenIdx(tok_idx)),
                ),
                timestamp=md.VSYSTimestamp.now(),
                attachment=md.Str(attachment),
                fee=md.ExecCtrtFee(fee),
            )
        )
        logger.debug(data)
        return data

    def withdraw(
        self,
        by: acnt.Account,
        ctrt_id: str,
        tok_idx: int,
        attachment: str = "",
        fee: int = md.ExecCtrtFee.DEFAULT,
    ) -> Dict[str, Any]:
        """
        withdraw withdraws the token from another contract to the action taker.

        Args:
            by (acnt.Account): The action taker.
            ctrt_id (str): The id of the contract to withdraw from.
            tok_idx (int): The index of the token within this contract to withdraw.
            attachment (str, optional): The attachment of this action. Defaults to "".
            fee (int, optional): The fee to pay for this action. Defaults to md.ExecCtrtFee.DEFAULT.

        Returns:
            Dict[str, Any]: The response returned by the Node API
        """
        data = by.execute_contract(
            tx.ExecCtrtFuncTxReq(
                ctrt_id=self._ctrt_id,
                func_id=self.FuncIdx.WITHDRAW,
                data_stack=de.DataStack(
                    de.CtrtAcnt(md.CtrtID(ctrt_id)),
                    de.Addr(md.Addr(by.addr.b58_str)),
                    de.INT32(md.TokenIdx(tok_idx)),
                ),
                timestamp=md.VSYSTimestamp.now(),
                attachment=md.Str(attachment),
                fee=md.ExecCtrtFee(fee),
            )
        )
        logger.debug(data)
        return data

    def supersede(
        self,
        by: acnt.Account,
        new_issuer: str,
        attachment: str = "",
        fee: int = md.ExecCtrtFee.DEFAULT,
    ) -> Dict[str, Any]:
        """
        supersede transfers the issuer role of the contract to a new account.

        Args:
            by (acnt.Account): The action taker.
            new_issuer (str): The account address of the new issuer.
            attachment (str, optional): The attachment of this action. Defaults to "".
            fee (int, optional): The fee to pay for this action. Defaults to md.ExecCtrtFee.DEFAULT.

        Returns:
            Dict[str, Any]: The response returned by the Node API
        """

        new_issuer_md = md.Addr(new_issuer)
        new_issuer_md.must_on(by.chain)

        data = by.execute_contract(
            tx.ExecCtrtFuncTxReq(
                ctrt_id=self._ctrt_id,
                func_id=self.FuncIdx.SUPERSEDE,
                data_stack=de.DataStack(
                    de.Addr(new_issuer_md),
                ),
                timestamp=md.VSYSTimestamp.now(),
                attachment=md.Str(attachment),
                fee=md.ExecCtrtFee(fee),
            )
        )
        logger.debug(data)
        return data
