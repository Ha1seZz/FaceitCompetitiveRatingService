"""Модуль фоновых задач."""

import functools

import httpx
from loguru import logger
from arq.worker import Retry

from app.infrastructure.db.repositories import (
    PlayerRepository,
    MatchHistoryRepository,
    PlayerStatsRepository,
)
from app.application import MatchHistoryService, PlayerService, PlayerStatsService


def calculate_backoff(job_try: int, base_delay: int = 5, max_delay: int = 300) -> int:
    """Расчет экспоненциального бэкоффа: base_delay * 2^(job_try - 1)."""
    delay = base_delay * (2 ** (job_try - 1))
    return min(delay, max_delay)


def with_arq_retry(func):
    """
    Декоратор для перехвата сетевых ошибок и автоматического
    управления повторами (Retry) в задачах ARQ.
    """

    @functools.wraps(func)
    async def wrapper(ctx, *args, **kwargs):
        job_try = ctx.get("job_try", 1)

        # Пытаемся получить идентификатор сущности (player_id или nickname) для понятных логов
        entity_id = kwargs.get("player_id") or kwargs.get("nickname")
        if not entity_id and args:
            entity_id = args[0]

        task_name = func.__name__

        try:
            return await func(ctx, *args, **kwargs)

        except httpx.HTTPStatusError as exc:
            status_code = exc.response.status_code

            # 429 Too Many Requests или серверные падения Faceit (5xx)
            if status_code == 429 or status_code >= 500:
                retry_after = exc.response.headers.get("Retry-After")
                if retry_after and retry_after.isdigit():
                    delay = int(retry_after)
                else:
                    delay = calculate_backoff(job_try)

                logger.warning(
                    "[{task}] Faceit API вернул статус {status}. Откладываем задачу ('{entity}') на {delay} сек.",
                    task=task_name,
                    status=status_code,
                    entity=entity_id,
                    delay=delay,
                )
                raise Retry(defer=delay)

            # Прочие ошибки (400, 401, 403, 404) не лечатся ретраями
            logger.error(
                "[{task}] Критическая ошибка HTTP {status} к Faceit для ('{entity}'): {err}",
                task=task_name,
                status=status_code,
                entity=entity_id,
                err=exc,
            )
            raise exc

        except Exception as exc:
            # Отлов прочих непредвиденных исключений (например, сбои БД или таймауты сети)
            logger.exception(
                "[{task}] Непредвиденная ошибка для ('{entity}'): {err}",
                task=task_name,
                entity=entity_id,
                err=exc,
            )
            delay = calculate_backoff(job_try)
            raise Retry(defer=delay)

    return wrapper


@with_arq_retry
async def task_refresh_match_history(
    ctx,
    player_id: str,
    limit: int,
    start_offset: int,
    lock_key: str,
) -> None:
    """Фоновая задача для обновления истории матчей игрока."""
    logger.info(
        "Начало фонового обновления матчей для игрока {player_id}",
        player_id=player_id,
    )
    session_factory = ctx["session_factory"]

    async with session_factory() as session:
        match_history_service = MatchHistoryService(
            match_history_repo=MatchHistoryRepository(session),
            player_repo=PlayerRepository(session),
            faceit_client=ctx["faceit_client"],
            session=session,
            redis=ctx["redis"],
            arq_pool=ctx["arq_pool"],
        )
        await match_history_service.process_background_refresh(
            player_id=player_id,
            limit=limit,
            start_offset=start_offset,
            lock_key=lock_key,
        )

    logger.info(
        "Фоновое обновление матчей для игрока {player_id} завершено.",
        player_id=player_id,
    )


@with_arq_retry
async def task_refresh_player(ctx, nickname: str, lock_key: str) -> None:
    """Фоновая задача для обновления информации о игроке."""
    logger.info(
        "Начало фонового обновления информации о игроке {nickname}",
        nickname=nickname,
    )
    session_factory = ctx["session_factory"]

    async with session_factory() as session:
        service = PlayerService(
            session=session,
            player_repo=PlayerRepository(session),
            faceit_client=ctx["faceit_client"],
            redis=ctx["redis"],
            arq_pool=ctx["arq_pool"],
        )
        await service._refresh_player_bg(nickname, lock_key)
    logger.info(
        "Фоновое обновление информации о игроке {nickname} завершено.",
        nickname=nickname,
    )


@with_arq_retry
async def task_refresh_stats(ctx, player_id: str, lock_key: str) -> None:
    """Фоновая задача для обновления статистики игрока."""
    logger.info(
        "Начало фонового обновления статистики для игрока {player_id}",
        player_id=player_id,
    )
    session_factory = ctx["session_factory"]

    async with session_factory() as session:
        service = PlayerStatsService(
            stats_repo=PlayerStatsRepository(session),
            faceit_client=ctx["faceit_client"],
            session=session,
            redis=ctx["redis"],
            arq_pool=ctx["arq_pool"],
        )
        await service._refresh_stats_bg(player_id=player_id, lock_key=lock_key)
    logger.info(
        "Фоновое обновление статистики для игрока {player_id} завершено.",
        player_id=player_id,
    )
