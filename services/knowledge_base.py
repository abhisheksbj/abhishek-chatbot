knowledge_base = [
    {
        "q": "What is the refund policy?",
        "a": "Ticketmaster's standard policy is no refunds unless the event is cancelled or postponed. Some events offer refund protection at purchase. If an event is cancelled, you'll automatically receive a refund to your original payment method."
    },
    {
        "q": "Can I transfer my tickets?",
        "a": "Yes, most tickets can be transferred digitally via your Ticketmaster account. Go to My Tickets, select the event, and choose Transfer. The recipient will get an email to accept the transfer."
    },
    {
        "q": "What are the service fees?",
        "a": "Service fees vary by event and venue. They typically include a facility charge and order processing fee. Fees are shown in full before you complete your purchase — there are no hidden charges."
    },
    {
        "q": "How do I pick up my tickets at will call?",
        "a": "Will call tickets are held at the venue box office. Bring your order confirmation and a valid photo ID matching the name on the order. Will call windows usually open 1–2 hours before the event."
    },
    {
        "q": "Are tickets mobile only?",
        "a": "Many venues and events now require mobile tickets. You'll receive a barcode in the Ticketmaster app. Make sure your phone is charged and you have the app installed before arriving at the venue."
    },
    {
        "q": "What happens if an event is postponed?",
        "a": "If an event is postponed, your tickets are typically valid for the new date. Ticketmaster will notify you by email. In many cases you'll be given the option to request a refund if the new date doesn't work for you."
    },
    {
        "q": "Can I resell my tickets?",
        "a": "Ticket resale availability depends on the event. Where resale is enabled, you can list tickets on Ticketmaster Fan-to-Fan Resale. Some events use non-transferable tickets to prevent resale."
    },
    {
        "q": "How do I get a receipt or invoice?",
        "a": "Your order confirmation email serves as your receipt. You can also view and print order details by logging into your Ticketmaster account and going to My Orders."
    },
    {
        "q": "What is Ticketmaster Fan Guarantee?",
        "a": "The Ticketmaster Fan Guarantee means every ticket sold through Ticketmaster is 100% verified and authentic. If there's ever an issue with your ticket at the door, Ticketmaster will make it right."
    },
    {
        "q": "Are there accessible seating options?",
        "a": "Yes, accessible and ADA-compliant seating is available for most events. When searching for tickets, look for the accessibility filter, or call the venue directly to arrange accessible accommodations."
    },
]


def search(query: str) -> list[dict]:
    query_lower = query.lower()
    results = []
    for item in knowledge_base:
        combined = (item["q"] + " " + item["a"]).lower()
        if any(word in combined for word in query_lower.split() if len(word) > 3):
            results.append(item)
    return results[:3]
