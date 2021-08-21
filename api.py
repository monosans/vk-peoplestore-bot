# -*- coding: utf-8 -*-
from random import uniform
from time import sleep

from loguru import logger
from requests import Session


class PeopleStore:
    def __init__(
        self,
        authorization: str,
        user_agent: str,
        min_delay: float = 6,
        max_delay: float = 8,
    ) -> None:
        """
        authorization (str): vk_access_token_settings...
        user_agent (str): User agent браузера, с которого был получен
            authorization.
        min_delay (float): Минимальная задержка между одинаковыми запросами в
            секундах.
        max_delay (float): Максимальная задержка между одинаковыми запросами в
            секундах.
        """
        self._s = Session()
        self._s.headers.update(
            {
                "Authorization": authorization,
                "Referer": f"https://peostore.mydzin.ru/?{authorization}",
                "User-Agent": user_agent,
                "x-vk-credentials": authorization,
            }
        )
        self._MIN_DELAY = min_delay
        self._MAX_DELAY = max_delay

    def buy_slave(self, slave_id: int) -> dict:
        """Покупка указанного раба."""
        return self._req(f"slave_id={slave_id}&_method=buySlave")

    def fetter_slave(self, slave_id: int) -> dict:
        """Покупка оков указанному рабу."""
        return self._req(f"slave_id={slave_id}&_method=fetterSlave")

    def job_slave(self, slave_id: int, job_name: str) -> dict:
        """Выдача работы указанному рабу."""
        return self._req(
            f"slave_id={slave_id}&job_name={job_name}&_method=jobSlave"
        )

    def sell_slave(self, slave_id: int) -> dict:
        """Продажа указанного раба."""
        return self._req(f"slave_id={slave_id}&_method=sellSlave")

    def start(self) -> dict:
        """Получение подробной информации о себе."""
        return self._req("id=0&_method=start")

    def top_users(self) -> dict:
        """Получение топа игроков."""
        return self._req("&_method=getTopUsers")

    def user(self, user_id: int) -> dict:
        """Получение информации об указанном пользователе."""
        return self._req(f"id={user_id}&_method=user")

    def _req(self, endpoint: str) -> dict:
        """Метод для отправки запросов серверу игры.

        Args:
            endpoint (str): Конечная точка.

        Returns:
            dict: Если получен корректный ответ от сервера, возвращает ответ,
                иначе {}.
        """
        try:
            r = self._s.get(
                f"https://peostore.mydzin.ru/api/_/?{endpoint}"
            ).json()
        except Exception as e:
            logger.error(f"{endpoint}: {e}")
            sleep(uniform(self._MIN_DELAY, self._MAX_DELAY))
            return self._req(endpoint)
        try:
            return r["payload"]
        except KeyError:
            try:
                error_message = r["error_message"]
            except KeyError:
                logger.error(f"{endpoint}: {r}")
            else:
                if error_message == "Вы совершаете много однотипных действий":
                    sleep(uniform(self._MIN_DELAY, self._MAX_DELAY))
                    return self._req(endpoint)
                if (
                    error_message
                    == "Текущая сессия истекла, попробуйте перезапустить приложение"
                ):
                    logger.error(
                        """
Сессия истекла. Нужно зайти в игру и купить любого раба.
Если это не помогает, значит в config введён неверный USER_AGENT"""
                    )
                else:
                    logger.error(f"{endpoint}: {error_message}")
        return {}
