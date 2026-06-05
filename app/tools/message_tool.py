from __future__ import annotations

from app.models import InlineKeyboardButton, InlineKeyboardMarkup


class MessageTool:
    def build_text(self, *, title: str, message: str) -> str:
        return f"*{title}*\n{message}"

    def build_keyboard(self, reminder_id: str) -> InlineKeyboardMarkup:
        return InlineKeyboardMarkup(
            inline_keyboard=[
                [
                    InlineKeyboardButton(text="✅ Feito", callback_data=f"done:{reminder_id}"),
                    InlineKeyboardButton(
                        text="❌ Não feito", callback_data=f"not_done:{reminder_id}"
                    ),
                ],
                [
                    InlineKeyboardButton(
                        text="⏰ Adiar 15min", callback_data=f"postponed:{reminder_id}"
                    )
                ],
            ]
        )

