import os
from twilio.rest import Client
from supabase import create_client


def get_supabase():
    return create_client(os.environ["SUPABASE_URL"], os.environ["SUPABASE_KEY"])


def get_subscribers(location: str) -> list[dict]:
    sb = get_supabase()
    result = (
        sb.table("subscribers")
        .select("*")
        .eq("active", True)
        .execute()
    )
    return [s for s in result.data if s["location"] in (location, "both")]


def send_sms(phone: str, message: str):
    client = Client(os.environ["TWILIO_ACCOUNT_SID"], os.environ["TWILIO_AUTH_TOKEN"])
    client.messages.create(
        body=message,
        from_=os.environ["TWILIO_PHONE"],
        to=phone,
    )


def format_message(location: str, flavors: list[str]) -> str:
    name = "Brooklyn" if location == "brooklyn" else "Manhattan"
    order_url = (
        "order.toasttab.com/online/caffe-panna"
        if location == "brooklyn"
        else "order.toasttab.com/online/caffe-panna-manhattan"
    )
    lines = "\n".join(f"• {f}" for f in flavors)
    return (
        f"Caffe Panna {name} — today's flavors:\n\n"
        f"{lines}\n\n"
        f"Order: {order_url}\n"
        f"Reply STOP to unsubscribe."
    )
