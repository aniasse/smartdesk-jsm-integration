"""
SmartDesk — étape de triage IA.

Classe un ticket Jira Service Management en JSON structuré avec Claude.
C'est l'implémentation de référence de la "couche IA" de l'intégration :
tu peux la lancer en standalone pour tester, puis reproduire le même appel
dans n8n via un node HTTP Request vers l'API Claude.

Approche : structured outputs (`client.messages.parse`) — l'équivalent moderne
et robuste du function calling pour de l'extraction/classification : Claude est
contraint de répondre dans le schéma Pydantic ci-dessous, validé automatiquement.
"""

import json
import os
import sys
import time
from typing import Literal

import anthropic
from pydantic import BaseModel


# --- Le format que Claude DOIT renvoyer (contrat de données) --------------
class Triage(BaseModel):
    category: Literal["Bug", "Access", "Billing", "How-to", "Outage"]
    priority: Literal["Low", "Medium", "High", "Critical"]
    sentiment: Literal["positive", "neutral", "negative"]
    summary: str          # 1-2 phrases
    suggested_reply: str  # brouillon de réponse pour l'agent support


SYSTEM = (
    "You triage IT support tickets for a service desk. "
    "Classify the ticket, judge its priority and the customer's sentiment, "
    "write a 1-2 sentence summary, and draft a short, polite reply the agent "
    "can send. Be concise and factual."
)

# claude-opus-4-8 = qualité max. Pour un triage haut-volume et moins cher,
# tu peux passer model="claude-haiku-4-5" (c'est ton choix de coût).
DEFAULT_MODEL = "claude-opus-4-8"


def triage(subject: str, body: str, model: str = DEFAULT_MODEL) -> tuple[Triage, int]:
    """Renvoie (Triage, latence_ms). Lève une exception en cas d'erreur API."""
    client = anthropic.Anthropic()  # lit ANTHROPIC_API_KEY dans l'environnement
    started = time.monotonic()
    response = client.messages.parse(
        model=model,
        max_tokens=1024,
        system=SYSTEM,
        messages=[
            {
                "role": "user",
                "content": f"Subject: {subject}\n\nDescription:\n{body}",
            }
        ],
        output_format=Triage,
    )
    latency_ms = int((time.monotonic() - started) * 1000)
    return response.parsed_output, latency_ms


if __name__ == "__main__":
    # Démo : pipe ton propre JSON {"subject":..,"body":..} ou utilise l'exemple.
    piped = "" if sys.stdin.isatty() else sys.stdin.read()
    if piped.strip():
        payload = json.loads(piped)
        subject, body = payload["subject"], payload["body"]
    else:
        subject = "Cannot log in to the portal"
        body = (
            "Since this morning I get 'invalid credentials' even with the right "
            "password. I already reset it twice. I have a client demo in one hour "
            "and I'm completely blocked. Please help fast."
        )

    if not os.getenv("ANTHROPIC_API_KEY"):
        sys.exit("⚠️  ANTHROPIC_API_KEY manquant. Fais : export ANTHROPIC_API_KEY=sk-ant-...")

    result, latency = triage(subject, body)
    print(json.dumps(result.model_dump(), indent=2, ensure_ascii=False))
    print(f"\n[triaged in {latency} ms]", file=sys.stderr)
