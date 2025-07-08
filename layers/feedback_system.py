import sqlite3
from typing import List, Dict
import logging

# Setup logging
logging.basicConfig(level=logging.INFO)

class FeedbackManager:
    VALID_LAYERS = [
        "nlu_primary",
        "nlu_secondary",
        "nlg_primary",
        "nlg_secondary",
        "stm_to_ltm",
        "stm_to_factual_memory",
        "self_thinking_layer",
        "text_to_voice_layer",
        "voice_to_text_layer"
    ]

    def __init__(self, db_name: str = "feedback.db"):
        self.db_name = db_name
        self._setup_database()

    def _setup_database(self):
        with sqlite3.connect(self.db_name) as conn:
            cursor = conn.cursor()

            # Drop tables for fresh development schema — remove in production
            cursor.execute("DROP TABLE IF EXISTS feedback_layers")
            cursor.execute("DROP TABLE IF EXISTS feedback")

            cursor.execute("""
            CREATE TABLE IF NOT EXISTS feedback (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                detected_feedback TEXT NOT NULL,
                summary TEXT,
                user_suggestion TEXT
            )
            """)

            cursor.execute("""
            CREATE TABLE IF NOT EXISTS feedback_layers (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                feedback_id INTEGER NOT NULL,
                layer_tag TEXT NOT NULL,
                FOREIGN KEY(feedback_id) REFERENCES feedback(id)
            )
            """)

    def store_feedback(
        self,
        detected_feedback: str,
        summary: str,
        layer_tags: List[str],
        user_suggestion: str
    ):
        with sqlite3.connect(self.db_name) as conn:
            cursor = conn.cursor()

            cursor.execute("""
                INSERT INTO feedback (detected_feedback, summary, user_suggestion)
                VALUES (?, ?, ?)
            """, (detected_feedback, summary, user_suggestion))

            feedback_id = cursor.lastrowid

            for tag in layer_tags:
                if tag in self.VALID_LAYERS:
                    cursor.execute("""
                        INSERT INTO feedback_layers (feedback_id, layer_tag)
                        VALUES (?, ?)
                    """, (feedback_id, tag))
                else:
                    logging.warning(f"⚠️ Invalid layer tag skipped: {tag}")

    def get_feedback_by_layer(self, layer_tag: str) -> List[Dict]:
        with sqlite3.connect(self.db_name) as conn:
            cursor = conn.cursor()

            cursor.execute("""
                SELECT f.id, f.detected_feedback, f.summary, f.user_suggestion
                FROM feedback f
                JOIN feedback_layers fl ON f.id = fl.feedback_id
                WHERE fl.layer_tag = ?
            """, (layer_tag,))

            results = cursor.fetchall()

        return [
            {
                "id": row[0],
                "detected_feedback": row[1],
                "summary": row[2],
                "user_suggestion": row[3]
            } for row in results
        ]

manager = FeedbackManager()