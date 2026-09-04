import argparse

from src.agent.runtime import run_ops_pilot


def main():

    parser = argparse.ArgumentParser(
        description="OpsPilot support-ticket triage system"
    )

    parser.add_argument(
        "--ticket",
        required=True,
        help="Support ticket text",
    )

    parser.add_argument(
        "--ticket-id",
        default="CLI-001",
        help="Ticket identifier",
    )

    args = parser.parse_args()

    state = run_ops_pilot(
        ticket_id=args.ticket_id,
        ticket_text=args.ticket,
    )

    print()
    print("=" * 60)
    print("OPSPILOT RESULT")
    print("=" * 60)

    print("Ticket:", state.ticket_text)
    print("Intent:", state.intent)
    print(
        "Intent confidence:",
        round(state.intent_confidence or 0, 3),
    )
    print(
        "Escalation probability:",
        round(state.escalation_probability or 0, 3),
    )

    print()
    print("Retrieved policies:")

    for document in state.retrieved_documents:
        print(
            f"- {document['source']} "
            f"(score={document['score']:.3f})"
        )

    print()
    print("Draft:")
    print(state.draft)

    print()
    print("Critic:", state.critic_status)
    print("Critic reason:", state.critic_reason)

    print()
    print("HITL required:", state.hitl_required)
    print("Final route:", state.final_route)

    print()
    print("Trace:")

    for item in state.trace:
        print("-", item)


if __name__ == "__main__":
    main()